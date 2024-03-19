from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scripts.question import Question

from typing import Dict, List

import json
import time

class KahootMaker:
    loading_page_time_seconds: float = 3
    _urls: Dict[str,str] = {
        'open_kahoot': r"https://create.kahoot.it/auth/login?brand_id=3330647&locale_id=1&return_to=https%3A%2F%2Fsupport.kahoot.com%2Fhc%2Fen-us%2Farticles%2F11064559523731-Kahoot-login&timestamp=1709577277",
        'create_kahoot': r"https://create.kahoot.it/creator",
        'share_kahoot': r'https://create.kahoot.it/my-library/kahoots/all',
    }
    _x_paths: Dict[str, str] = {
        'create_empty_kahoot_button': r'//*[@id="kahoot-creation-flow-dialog"]/div/div[2]/div/div[3]/button',
        'create_empty_kahoot_button_2': r'//*[@id="template-dialog"]/div/div[2]/div/div/button',
        'choices_box': r'//*[@id="root"]/div/div/main/div/div/div[2]/div/div/div',
        'config_side_bar': r'//*[@id="question-action-menu"]',
        'question_input': r'//*[@id="id_41e14f36-70a8-4a77-b5c2-9b7c0ca11d2e"]/p',
        'button0': r'//*[@id="root"]/div/div/main/div/div/div[2]/div/div/div/div[1]/div[2]/button',
        'title_input': r'//*[@id="7c56632c-0bfa-43b2-b10a-fd1bcecde4a6"]',
        'description_input': r'//*[@id="e806b7f5-c990-45a9-ad1d-e0a510dfc14c"]',
        'publish_button': r'//*[@id="dialog-add-title"]/div/div[4]/button[2]',
        'options_button': r'//*[@id="action-menu__toggle-kahootCardActionMenu8c639f37-b135-4181-b080-ee7b4bebbf7d"]/span',
        'visibility_button': r'//*[@id="action-menu__toggle-kahootCardVisibilityActionMenu-8c639f37-b135-4181-b080-ee7b4bebbf7d"]',
        'public_button': r'//*[@id="kahootCardVisibilityActionMenu-8c639f37-b135-4181-b080-ee7b4bebbf7d"]/span/li[2]',
        'share_button': r'//*[@id="share"]/div/span',
        'kahoot_link': r'//*[@id="4d7494fe-9c4d-4419-b160-3b7f7f6d904b"]',
        'save_popup': r'//*[@id="dialog-add-title"]/div',
        'kahoots': r'//*[@id="library-content"]/div[2]/div[3]',
        'open_side_bar': r'//*[@id="action-menu__toggle-question-action-menu"]',
        'set_time_popup': r'//*[@id="dialog"]',
        'done_button': r'//*[@id="dialog"]/div/div[3]/button[2]',
        'add_question_button': r'//*[@id="main-content"]/div[2]/div/span/button'
    }

    def __init__(self, **kwargs):
        self.driver: webdriver.Chrome = None

    def open_browser(self) -> bool:
        options = Options()

        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = Chrome(options=options)

        return True

    def open_kahoot(self) -> bool:
        return self._open_web_page(self._urls['open_kahoot'])

    def open_create_kahoot(self) -> bool:
        return self._open_web_page(self._urls['create_kahoot'])
    
    def _open_web_page(self, url: str) -> bool:
        if not self.driver:
            return False
        self.driver.get(url)
        time.sleep(self.loading_page_time_seconds)
        return True

    def login(self) -> bool:
        if not self.driver:
            return False
        
        if self.driver.current_url != self._urls['open_kahoot']:
            return False
        
        # load login information
        with open('secrets.json', 'r') as secrets:
            dict_secrts: Dict[str,str] = json.loads(secrets.read())['Login']

        # insert username
        username_field = self.driver.find_element(By.ID, 'username')
        username_field.send_keys(dict_secrts['Username'])

        # insert passwaord
        password_field = self.driver.find_element(By.ID, 'password')
        password_field.send_keys(dict_secrts['Password'])

        # click on login
        login_button = self.driver.find_element(By.ID, 'login-submit-btn')
        login_button.click()

        # ignoring possible request for verifying email
        time.sleep(self.loading_page_time_seconds)

        self._close_pop_up()
        self._skip_email_verification()

        time.sleep(self.loading_page_time_seconds)

        return True
    
    def _close_pop_up(self) -> bool:
        if not self.driver:
            return False

        buttons: List[WebElement] = self.driver.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            if button.text == 'Cancel':
                button.click()
                break
        else:
            return False
        return True
    
    def _skip_email_verification(self) -> bool:
        if not self.driver:
            return False
        
        if 'verify_email' in self.driver.current_url:
            return True
        
        buttons: List[WebElement] = self.driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if "Next time" == button.text:
                button.click()
                break
        else:
            return False
        return True

    def create_kahoot(self) -> bool:
        if not self.driver:
            return False
        
        self.open_create_kahoot()

        for button_functionality in ['create_empty_kahoot_button', 'create_empty_kahoot_button_2']:
            template_button: WebElement = self.driver.find_element(By.XPATH, self._x_paths[button_functionality])
            template_button.click()
            time.sleep(self.loading_page_time_seconds)

    def add_question(self, question: Question, is_first_question: bool) -> bool:
        
        buttons: List[WebElement] = self.driver.find_elements(By.TAG_NAME, "button")
        selection_box: WebElement = None
        is_time_limit_set: bool = False

        # Create new question
        if not is_first_question:
            self.driver.find_element(By.XPATH, self._x_paths['add_question_button']).click()
            
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.text == 'Quiz':
                    button.click()
                    break
            else:
                return False
   
        # Select theme

        # Add question
        question_field = [p for p in self.driver.find_elements(By.TAG_NAME, 'p') if p.get_attribute('data-placeholder') == 'Start typing your question'][0]
        question_field.send_keys(question.question)
            
        # Add choices
        self.add_choices(question.choices, question.correct)

        # Select quiz rules
        #self.driver.find_element(By.XPATH, self._x_paths['open_side_bar']).click()
        #time.sleep(0.1)
        
        '''for element in [element for element in side_bar.find_elements(By.TAG_NAME, 'span') if 'icon__Icon' in element.get_attribute('class')][1::2][1:3]:
            element.click()
            selection_box = side_bar.find_element(By.CLASS_NAME, 'css-1yc5hu0-menu')
            options = selection_box.find_elements(By.TAG_NAME, 'div')[4::4]
            if is_time_limit_set:
                if question.pontuation_system != 0:
                    options[question.pontuation_system].click()
                else:
                    element.click()
            else:
                if question.time_limit != 2:
                    options[question.time_limit].click()
                else:
                    element.click()
                is_time_limit_set = True
        '''
        self.driver.find_element(By.XPATH, self._x_paths['open_side_bar']).click()
        side_bar: WebElement = self.driver.find_element(By.XPATH, self._x_paths['config_side_bar'])
        buttons2 = side_bar.find_elements(By.TAG_NAME, 'button')
        buttons2[1].click()
        popup = self.driver.find_element(By.XPATH, self._x_paths['set_time_popup'])
        button3 = popup.find_elements(By.TAG_NAME, 'button')
        button3[question.time_limit].click()
        try:
            self.driver.find_element(By.XPATH, self._x_paths['done_button']).click()
        except:
            pass

        self.driver.find_element(By.XPATH, self._x_paths['open_side_bar']).click()
        side_bar: WebElement = self.driver.find_element(By.XPATH, self._x_paths['config_side_bar'])
        buttons2 = side_bar.find_elements(By.TAG_NAME, 'button')
        buttons2[2].click()
        popup = self.driver.find_element(By.XPATH, self._x_paths['set_time_popup'])
        button3 = popup.find_elements(By.TAG_NAME, 'button')
        button3[question.pontuation_system].click()
        try:
            self.driver.find_element(By.XPATH, self._x_paths['done_button']).click()
        except:
            pass

        # Add image
            
        # Delete initial question
        time.sleep(0.2)
        return True

    def add_questions(self, questions: List[Question]) -> bool:
        is_first_question: bool = True
        for question in questions:
            self.add_question(question, is_first_question)
            is_first_question = False

    def set_correct_choice(self, correct: int):
        if not self.driver:
            return False
        
        if 'creator' not in self.driver.current_url:
            return False
        
        if correct:
            button: List[WebElement] = self.driver.find_element(By.ID, str(correct))
        else:
            button: List[WebElement] = self.driver.find_element(By.XPATH, self._x_paths['button0'])
        button.click()
        return True

    def select_question_type(self, question_type: str) -> bool:
        pass

    def add_choices(self, alternatives: List[str], correct: int) -> bool:
        if not self.driver:
            return False
        
        if 'creator' not in self.driver.current_url:
            return False
        
        choices_box: WebElement = self.driver.find_element(By.XPATH, self._x_paths['choices_box'])
        for i, text_entry in enumerate(choices_box.find_elements(By.TAG_NAME, 'p')):
            if i < len(alternatives):
                text_entry.send_keys(alternatives[i])
            

        return self.set_correct_choice(correct)

    def add_image(self, tag)-> bool:
        pass

    def publish_kahoot(self, title: str, description: str) -> str:
        if not self.driver:
            return ''
        
        time.sleep(self.loading_page_time_seconds)
        buttons: List[WebElement] = self.driver.find_elements(By.TAG_NAME, 'button')
        save_button: WebElement = None
        for button in buttons:
            if button.text.lower() == 'save':
                save_button = button
                break
        save_button.click()

        
        pop_up = self.driver.find_element(By.XPATH, self._x_paths['save_popup'])
        
        time.sleep(0.3)
        title_input = pop_up.find_element(By.TAG_NAME, 'input')
        title_input.send_keys(title)

        #description_input = self.driver.find_element(By.XPATH, self._x_paths['description_input'])
        #description_input.send_keys(title)

        publish_button = self.driver.find_element(By.XPATH, self._x_paths['publish_button'])
        publish_button.click()

        time.sleep(1)
        return self._share_kahoot()

    def _share_kahoot(self):
        if not self.driver:
            return ''
        

        
        time.sleep(self.loading_page_time_seconds)


        self.driver.get(self._urls['share_kahoot'])

        time.sleep(self.loading_page_time_seconds)
        kahoots = self.driver.find_element(By.XPATH, self._x_paths['kahoots'])
        kahoot = kahoots.find_elements(By.TAG_NAME, 'div')[1]
        buttons: List[WebElement] = kahoot.find_elements(By.TAG_NAME, 'button')

        #buttons[1].click() - Config button
        buttons[2].click()
        time.sleep(0.2)
        labels = self.driver.find_elements(By.TAG_NAME, 'label')
        for label in labels:
            if label.text == 'Public':
                label.click()

        buttons[1].click()
        self.driver.find_element(By.ID, 'share').click()

        time.sleep(0.2)

        link = self.driver.find_elements(By.TAG_NAME,'input')[-1].get_attribute('value')
        return link

    def run(self, title: str, questions: List[Question]) -> str:        
        self.open_browser()
        self.open_kahoot()
        self.login()
        self.create_kahoot()
        self.add_questions(questions)
        self.publish_kahoot(title=title, description='')
        return self._share_kahoot()
