import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TodoAppTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize Chrome (you can also use Firefox or Edge)
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        # Start Flask app manually before running this test
        cls.base_url = "http://127.0.0.1:5001/"

    def test_1_add_task(self):
        driver = self.driver
        driver.get(self.base_url)
        
        # Find input box and add a task
        input_box = driver.find_element(By.NAME, "task")
        input_box.send_keys("Write Selenium Test")
        input_box.send_keys(Keys.RETURN)
        
        time.sleep(1)  # wait for page reload
        # Verify task is added
        tasks = driver.find_elements(By.XPATH, "//p[contains(text(),'Write Selenium Test')]")
        self.assertTrue(len(tasks) > 0, "Task not added!")

    def test_2_mark_done_and_undo(self):
        driver = self.driver
        driver.get(self.base_url)

        # Click the "Done" button for the first task
        done_button = driver.find_element(By.XPATH, "//button[contains(text(),'Done')]")
        done_button.click()
        time.sleep(1)

        # Verify task text has line-through class
        task = driver.find_element(By.XPATH, "//p[contains(@class,'line-through')]")
        self.assertIsNotNone(task, "Task was not marked as done")

        # Now click "Undo"
        undo_button = driver.find_element(By.XPATH, "//button[contains(text(),'Undo')]")
        undo_button.click()
        time.sleep(1)

        # Verify line-through removed
        undone_task = driver.find_element(By.XPATH, "//p[not(contains(@class,'line-through'))]")
        self.assertIsNotNone(undone_task, "Task was not undone")

    def test_3_delete_task(self):
        driver = self.driver
        driver.get(self.base_url)

        # Count tasks before delete
        tasks_before = driver.find_elements(By.XPATH, "//p")
        initial_count = len(tasks_before)
        self.assertGreater(initial_count, 0, "No tasks available to delete")

        # Click the Delete link for the first task
        delete_link = driver.find_element(By.XPATH, "//a[contains(text(),'Delete')]")
        delete_link.click()

        # Wait until task count decreases
        WebDriverWait(driver, 5).until(
            lambda d: len(d.find_elements(By.XPATH, "//p")) < initial_count
        )

        tasks_after = driver.find_elements(By.XPATH, "//p")
        self.assertLess(len(tasks_after), initial_count, "Task was not deleted")


        @classmethod
        def tearDownClass(cls):
            cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
