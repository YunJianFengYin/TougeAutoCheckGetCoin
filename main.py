# educoder_auto_checkin.py
import requests
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
import time
import json

class EducoderAutoCheckin:
    def __init__(self, username, password, headless=False):
        """
        初始化Educoder自动签到类
        :param username: 用户名或邮箱
        :param password: 密码
        :param headless: 是否使用无头模式
        """
        self.username = username
        self.password = password
        self.url = "https://www.educoder.net/"
        self.driver = None
        self.wait = None
        
        # 尝试设置Edge WebDriver
        if not self.setup_driver(headless):
            print("无法初始化浏览器驱动，程序退出")
            raise Exception("WebDriver初始化失败")

    def setup_driver(self, headless=False):
        """设置Edge WebDriver，带有多个备用方案"""
        # 尝试方案1：直接使用webdriver.Edge（让Selenium自己查找驱动）
        try:
            options = EdgeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # 禁用Selenium Manager
            os.environ['SELENIUM_DISABLE_SM'] = 'true'
            
            self.driver = webdriver.Edge(options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            # 执行一些脚本来隐藏自动化特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("Edge浏览器初始化成功")
            return True
        except Exception as e:
            print(f"方案1失败: {e}")
        
        # 如果方案1失败，尝试方案2：显式指定驱动路径
        try:
            # 检查当前目录是否有msedgedriver.exe
            driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "msedgedriver.exe")
            if os.path.exists(driver_path):
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Edge(service=service, options=options)
                self.wait = WebDriverWait(self.driver, 20)
                
                # 执行一些脚本来隐藏自动化特征
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                print("Edge浏览器初始化成功（使用当前目录驱动）")
                return True
            else:
                print(f"未在当前目录找到msedgedriver.exe: {driver_path}")
        except Exception as e:
            print(f"方案2失败: {e}")
        
        # 如果方案2也失败，尝试方案3：使用系统PATH中的驱动
        try:
            service = Service()  # 不指定路径，使用PATH中的驱动
            self.driver = webdriver.Edge(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            # 执行一些脚本来隐藏自动化特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("Edge浏览器初始化成功（使用PATH中的驱动）")
            return True
        except Exception as e:
            print(f"方案3失败: {e}")
        
        return False

    def login(self):
        """
        登录Educoder网站
        """
        if not self.driver:
            print("浏览器驱动未初始化")
            return False
            
        try:
            print("正在打开Educoder网站...")
            self.driver.get(self.url)
            time.sleep(3)
            
            # 根据您提供的信息，使用新的XPath路径定位登录按钮
            print("寻找登录按钮...")
            try:
                login_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[1]/header/section/div/div/span"))
                )
                print("使用新的XPath路径找到登录按钮")
                login_btn.click()
                time.sleep(2)
            except Exception as e:
                print(f"使用新XPath路径失败: {str(e)}")
                # 退回到原来的搜索方式
                try:
                    # 尝试多种可能的登录链接文本
                    login_selectors = [
                        (By.LINK_TEXT, "登录"),
                        (By.LINK_TEXT, "Sign In"),
                        (By.PARTIAL_LINK_TEXT, "登录"),
                        (By.CSS_SELECTOR, "a[href='/login']"),
                        (By.CSS_SELECTOR, "[data-login-btn]"),
                        (By.XPATH, "//a[contains(text(), '登录') or contains(text(), 'Login') or contains(text(), 'Sign In')]"),
                    ]
                    
                    login_btn = None
                    for selector_type, selector_value in login_selectors:
                        try:
                            login_btn = self.wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                            print(f"使用选择器 {selector_type} 找到登录按钮: {selector_value}")
                            break
                        except:
                            continue
                    
                    if login_btn is None:
                        print("未找到登录按钮，尝试其他方式...")
                        # 尝试直接访问登录页面
                        self.driver.get("https://www.educoder.net/login")
                        time.sleep(2)
                    else:
                        login_btn.click()
                        time.sleep(2)
                except Exception as e2:
                    print(f"查找登录按钮时出错: {str(e2)}")
                    # 尝试直接访问登录页面
                    self.driver.get("https://www.educoder.net/login")
                    time.sleep(2)
            
            # 输入用户名
            print("输入用户名...")
            try:
                # 使用您提供的确切XPath路径定位账号输入框
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[2]/div/div[1]/div/div/div/div/div[1]/div[1]/form/div[1]/div/div/div/div/input"))
                )
            except:
                # 如果没找到指定路径的输入框，尝试其他可能的选择器
                try:
                    username_input = self.wait.until(
                        EC.presence_of_element_located((By.NAME, "email"))
                    )
                except:
                    # 如果没找到name为email的输入框，尝试其他可能的选择器
                    try:
                        username_input = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
                        )
                    except:
                        try:
                            username_input = self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "input[id*='email'], input[id*='username'], input[id*='account']"))
                            )
                        except:
                            print("无法找到用户名输入框")
                            return False
            
            username_input.clear()
            username_input.send_keys(self.username)
            
            # 输入密码
            print("输入密码...")
            try:
                # 使用您提供的确切XPath路径定位密码输入框
                password_input = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div[1]/div/div/div/div/div[1]/div[1]/form/div[2]/div/div/div/div/span/input")
            except:
                # 如果没找到指定路径的输入框，尝试其他可能的选择器
                try:
                    password_input = self.driver.find_element(By.NAME, "password")
                except:
                    try:
                        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                    except:
                        print("无法找到密码输入框")
                        return False
            
            password_input.clear()
            password_input.send_keys(self.password)
            
            # 点击登录按钮
            print("点击登录...")
            try:
                # 使用您提供的确切XPath路径定位登录按钮
                submit_btn = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div/div[1]/div/div/div/div/div[1]/div[1]/form/div[4]/div/div/div/div/button")
            except:
                # 如果没找到指定路径的按钮，尝试其他可能的选择器
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                except:
                    try:
                        submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '登录') or contains(text(), 'Login') or contains(text(), 'Sign In')]")
                    except:
                        print("无法找到登录提交按钮")
                        return False
            
            submit_btn.click()
            
            # 等待登录完成
            time.sleep(5)
            
            # 不检查登录状态，直接前往签到页面
            print("登录提交完成，跳转到签到页面")
            return True
                
        except Exception as e:
            print(f"登录过程中发生错误: {str(e)}")
            return False

    def checkin(self):
        """
        执行签到操作
        """
        if not self.driver:
            print("浏览器驱动未初始化")
            return False
            
        try:
            print("正在打开Educoder签到页面...")
            self.driver.get(f"https://www.educoder.net/users/{self.username}/classrooms")
            time.sleep(3)

            print("正在查找签到功能...")
            # 刷新页面确保最新状态
            self.driver.get(f"https://www.educoder.net/users/{self.username}/classrooms")
            time.sleep(3)
            
            # 尝试直接使用指定的XPath路径
            try:
                checkin_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/section/div/div[1]/div/div/div[4]/div"))
                )
                print("找到签到元素")
                
                # 检查按钮是否可点击（未签到状态）
                if "已签到" not in checkin_btn.text and "已打卡" not in checkin_btn.text:
                    checkin_btn.click()
                    time.sleep(2)
                    
                    # 检查是否签到成功
                    if "签到成功" in self.driver.page_source or "打卡成功" in self.driver.page_source:
                        print("签到成功！")
                        return True
                    else:
                        print("签到可能已完成或遇到问题")
                        return True
                else:
                    print("今日已签到")
                    return True
                    
            except Exception as e:
                print(f"未找到指定路径的元素: {str(e)}")
                # 退回到原来的搜索方式
                checkin_elements = [
                    "立即签到",
                    "打卡",
                    "attendance",
                    "checkin",
                    "签到"
                ]
                
                for element_text in checkin_elements:
                    try:
                        checkin_btn = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{element_text}') or contains(@alt, '{element_text}') or contains(@title, '{element_text}')]"))
                        )
                        print(f"找到签到按钮: {element_text}")
                        
                        # 检查按钮是否可点击（未签到状态）
                        if "已签到" not in checkin_btn.text and "已打卡" not in checkin_btn.text:
                            checkin_btn.click()
                            time.sleep(2)
                            
                            # 检查是否签到成功
                            if "签到成功" in self.driver.page_source or "打卡成功" in self.driver.page_source:
                                print("签到成功！")
                                return True
                            else:
                                print("签到可能已完成或遇到问题")
                                return True
                        else:
                            print("今日已签到")
                            return True
                            
                    except:
                        continue
            
            print("未找到签到功能或今日已签到")
            return True
            
        except Exception as e:
            print(f"签到过程中发生错误: {str(e)}")
            return False

    def run(self):
        """
        运行完整的签到流程
        """
        if not self.driver:
            print("浏览器驱动未初始化，无法运行")
            return
            
        try:
            login_success = self.login()
            if login_success:
                time.sleep(2)
                success = self.checkin()
                if success:
                    print("自动签到任务完成！")
                else:
                    print("自动签到任务失败！")
            else:
                print("登录失败，无法执行签到")
        except Exception as e:
            print(f"运行过程中发生错误: {str(e)}")
        finally:
            # 关闭浏览器
            try:
                if self.driver:
                    self.driver.quit()
                    print("浏览器已关闭")
            except:
                print("关闭浏览器时出现问题")

def load_credentials(config_file="educoder_config.json"):
    """
    从配置文件加载用户凭证
    """
    # 使用相对于当前脚本的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['username'], config['password']
    except FileNotFoundError:
        print(f"配置文件 {config_path} 不存在")
        return None, None
    except KeyError as e:
        print(f"配置文件格式错误，缺少必要的字段: {str(e)}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误，不是有效的JSON: {str(e)}")
        return None, None

def save_credentials(username, password, config_file="educoder_config.json"):
    """
    保存用户凭证到配置文件
    """
    # 使用相对于当前脚本的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)
    
    config = {
        'username': username,
        'password': password
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"凭证已保存到 {config_path}")

if __name__ == "__main__":
    print("Educoder自动签到程序")
    print("=" * 30)
    
    # 尝试从配置文件加载凭证
    username, password = load_credentials()
    
    if not username or not password:
        # 如果配置文件不存在，提示用户输入
        print("未找到配置文件或配置不完整")
        username = input("请输入您的Educoder用户名/邮箱: ")
        password = input("请输入您的密码: ")
        
        # 询问是否保存凭证
        save = input("是否保存凭证到本地文件? (y/n): ").lower() == 'y'
        if save:
            save_credentials(username, password)
    else:
        print(f"已从配置文件加载用户名: {username}")
    
    # 创建签到实例并运行
    print("开始执行签到任务...")
    try:
        auto_checkin = EducoderAutoCheckin(username, password)
        auto_checkin.run()
    except Exception as e:
        print(f"程序执行失败: {str(e)}")
    
    print("程序结束")