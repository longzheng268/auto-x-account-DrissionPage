# -*- coding: utf-8 -*-
"""
Twitter/X 自动注册模块
基于 undetected-chromedriver 实现，提供更强的反检测能力
"""
import logging
import random
import time
import os
from typing import Optional, Dict, List
from pathlib import Path

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class TwitterRegister:
    """Twitter/X 自动注册器 - undetected-chromedriver 实现"""
    
    def __init__(self, service, page: Optional[uc.Chrome] = None, 
                 browser_path: Optional[str] = None, use_incognito: bool = False):
        """
        初始化注册器
        
        Args:
            service: 服务接口
            page: uc.Chrome 页面对象（可选）
            browser_path: 浏览器路径（可选，自动检测）
            use_incognito: 是否使用无痕模式
        """
        self.service = service
        self.page = page
        self.browser_path = browser_path
        self.use_incognito = use_incognito
        
        # 注册信息
        self.email = None
        self.password = None
        self.name = None
        self.birthday = None
        self.username = None
        
        logger.info("Twitter注册器已初始化（undetected-chromedriver实现）")
    
    def _ensure_page(self):
        """确保页面对象已创建"""
        if self.page is None:
            logger.info("=" * 60)
            logger.info("启动浏览器（undetected-chromedriver）")
            logger.info("=" * 60)
            
            # 最小化配置
            options = uc.ChromeOptions()
            options.add_argument('--lang=zh-CN')
            options.add_argument('--disable-popup-blocking')
            
            # 查找项目内置 Chrome
            project_dir = Path(__file__).parent.parent
            project_chrome = project_dir / "twitter_auto_register" / "chrome-win" / "chrome.exe"
            
            if not project_chrome.exists():
                logger.error(f"❌ 项目 Chrome 不存在: {project_chrome}")
                raise FileNotFoundError(f"请确保 Chrome 位于: {project_chrome}")
            
            logger.info("⚡ undetected-chromedriver 配置:")
            logger.info(f"   - 使用项目 Chrome: {project_chrome.name}")
            logger.info("   - 自动下载匹配 ChromeDriver")
            logger.info("   - 自动修补移除自动化特征")
            
            try:
                logger.info("")
                logger.info("正在启动浏览器...")
                
                # 使用 browser_executable_path 指定 Chrome
                self.page = uc.Chrome(
                    options=options,
                    browser_executable_path=str(project_chrome),
                    use_subprocess=True,
                    headless=False,
                )
                
                # 设置窗口大小
                width = random.randint(1024, 1440)
                height = random.randint(768, 900)
                self.page.set_window_size(width, height)
                
                # CDP 反检测
                self.page.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['zh-CN', 'zh', 'en']
                        });
                    """
                })
                
                logger.info(f"✓ 浏览器启动成功 ({width}x{height})")
                logger.info(f"✓ undetected-chromedriver 反检测已激活")
                
            except Exception as e:
                logger.error(f"浏览器启动失败: {e}")
                raise

    def register(self) -> Dict:
        """执行完整的注册流程"""
        try:
            self._ensure_page()
            
            logger.info("=" * 60)
            logger.info("开始 Twitter/X 注册流程")
            logger.info("=" * 60)
            
            self.service.report_status('started', '注册流程启动')
            
            # 1. 访问注册页面
            self.service.report_status('visit_page', '正在访问注册页面')
            if not self._visit_signup_page():
                return self._error_result("访问注册页面失败")
            
            # 2. 点击创建账号
            if not self._click_create_account():
                return self._error_result("点击创建账号失败")
            
            # 3. 切换到邮箱注册
            if not self._switch_to_email_signup():
                return self._error_result("切换邮箱注册失败")
            
            # 4. 获取邮箱
            logger.info("步骤4: 准备获取邮箱和密码...")
            self.service.report_status('need_email', '准备获取邮箱和密码')
            self._random_wait(0.5, 1)
            
            self.email, self.password = self.service.request_email()
            logger.info(f"获取到邮箱: {self.email}")
            
            # 5. 填写表单
            self.service.report_status('filling_form', '正在填写注册表单', {
                'email': self.email,
                'name': self.name
            })
            if not self._fill_signup_form():
                return self._error_result("填写注册表单失败")
            
            # 6. 人机验证
            self.service.report_status('need_captcha', '需要人机验证')
            if not self._handle_captcha():
                return self._error_result("处理人机验证失败")
            
            # 7. 邮箱验证码
            logger.info("步骤7: 准备输入邮箱验证码...")
            self.service.report_status('need_email_code', '准备输入验证码', {'email': self.email})
            if not self._input_email_code():
                return self._error_result("输入邮箱验证码失败")
            
            # 8. 设置密码
            self.service.report_status('setting_password', '正在设置密码')
            if not self._set_password():
                return self._error_result("设置密码失败")
            
            # 9. 跳过头像
            if not self._skip_profile_photo():
                return self._error_result("跳过头像失败")
            
            # 10. 设置用户名
            self.service.report_status('setting_username', '正在设置用户名')
            if not self._set_username():
                return self._error_result("设置用户名失败")
            
            # 11. 跳过可选步骤
            if not self._skip_optional_steps():
                return self._error_result("跳过可选步骤失败")
            
            logger.info("=" * 60)
            logger.info("✓ Twitter/X 注册成功！")
            logger.info(f"邮箱: {self.email}")
            logger.info(f"用户名: {self.username}")
            logger.info("=" * 60)
            
            self.service.report_status('completed', '注册成功', {
                'email': self.email,
                'username': self.username
            })
            
            return {
                'success': True,
                'email': self.email,
                'password': self.password,
                'username': self.username
            }
            
        except Exception as e:
            logger.error(f"注册失败: {str(e)}", exc_info=True)
            return self._error_result(f"异常: {str(e)}")

    def _visit_signup_page(self) -> bool:
        """访问注册页面"""
        try:
            logger.info("步骤1: 访问注册页面")
            self.page.get('https://x.com/i/flow/signup')
            self._random_wait(3, 5)
            
            # 检查重试按钮
            self._handle_retry_if_exists()
            
            logger.info("✓ 注册页面访问成功")
            return True
        except Exception as e:
            logger.error(f"访问注册页面失败: {e}")
            return False

    def _click_create_account(self) -> bool:
        """点击创建账号按钮"""
        try:
            logger.info("步骤2: 点击创建账号按钮")
            self._random_wait(2, 3)
            self._handle_retry_if_exists()
            
            # 查找按钮
            buttons = self.page.find_elements(By.TAG_NAME, 'button')
            logger.info(f"找到 {len(buttons)} 个按钮")
            
            for btn in buttons:
                try:
                    text = btn.text
                    if text and ('创建账号' in text or 'Create account' in text or 'Sign up' in text):
                        # 排除 Google/Apple 登录
                        if 'Google' in text or 'Apple' in text:
                            continue
                            
                        logger.info(f"找到目标按钮: '{text}'")
                        self.page.execute_script("arguments[0].scrollIntoView();", btn)
                        self._random_wait(0.5, 1)
                        btn.click()
                        logger.info("✓ 点击成功")
                        self._random_wait(2, 4)
                        self._handle_retry_if_exists()
                        return True
                except:
                    continue
            
            logger.warning("未找到创建账号按钮")
            return False
        except Exception as e:
            logger.error(f"点击创建账号失败: {e}")
            return False

    def _switch_to_email_signup(self) -> bool:
        """切换到邮箱注册"""
        try:
            logger.info("步骤3: 切换到邮箱注册")
            # 查找 "改用电子邮件" 链接
            try:
                xpath = "//span[contains(text(), '改用电子邮件') or contains(text(), 'Use email instead')]"
                email_link = WebDriverWait(self.page, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                email_link.click()
                logger.info("✓ 已切换到邮箱注册")
                self._random_wait(1, 2)
                return True
            except TimeoutException:
                logger.info("可能已经是邮箱注册模式或未找到切换链接")
                return True
        except Exception as e:
            logger.warning(f"切换邮箱注册失败: {e}")
            return True

    def _fill_signup_form(self) -> bool:
        """填写注册表单"""
        try:
            logger.info("步骤5: 填写注册表单")
            
            self.name = self._generate_random_name()
            self.birthday = self._generate_random_birthday()
            
            logger.info(f"姓名: {self.name}")
            logger.info(f"邮箱: {self.email}")
            
            # 填写姓名
            try:
                name_input = WebDriverWait(self.page, 10).until(
                    EC.presence_of_element_located((By.NAME, "name"))
                )
                name_input.send_keys(self.name)
                self._random_wait(0.5, 1)
            except TimeoutException:
                logger.warning("未找到姓名输入框")
            
            # 填写邮箱
            try:
                email_input = self.page.find_element(By.CSS_SELECTOR, 'input[type="email"]')
                email_input.send_keys(self.email)
                self._random_wait(0.5, 1)
            except NoSuchElementException:
                logger.warning("未找到邮箱输入框")
            
            # 填写生日
            self._fill_birthday()
            
            # 点击下一步
            try:
                next_btn = WebDriverWait(self.page, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '下一步') or contains(text(), 'Next')]"))
                )
                next_btn.click()
                logger.info("✓ 表单已提交")
                self._random_wait(3, 5)
                self._handle_retry_if_exists()
                
                # 检查后续页面状态
                return self._check_post_submit_status()
                
            except TimeoutException:
                logger.warning("未找到下一步按钮")
                return False
                
        except Exception as e:
            logger.error(f"填写表单失败: {e}")
            return False

    def _fill_birthday(self):
        """填写生日"""
        try:
            year, month, day = self.birthday
            logger.info(f"填写生日: {year}-{month}-{day}")
            
            # 月份
            try:
                month_select = self.page.find_element(By.ID, "SELECTOR_1")
                month_select.send_keys(str(month))
                self._random_wait(0.2, 0.5)
            except: pass
            
            # 日期
            try:
                day_select = self.page.find_element(By.ID, "SELECTOR_2")
                day_select.send_keys(str(day))
                self._random_wait(0.2, 0.5)
            except: pass
            
            # 年份
            try:
                year_select = self.page.find_element(By.ID, "SELECTOR_3")
                year_select.send_keys(str(year))
                self._random_wait(0.2, 0.5)
            except: pass
            
            logger.info("✓ 生日填写完成")
        except Exception as e:
            logger.warning(f"填写生日失败: {e}")

    def _check_post_submit_status(self) -> bool:
        """检查提交后的页面状态"""
        logger.info("检测页面状态...")
        for _ in range(15):
            try:
                # 检查错误
                error_ele = self.page.find_elements(By.XPATH, "//span[contains(text(), '出错') or contains(text(), 'Error')]")
                if error_ele:
                    logger.warning(f"→ 检测到错误: {error_ele[0].text}")
                    return False
                
                # 检查验证码输入框
                if self.page.find_elements(By.NAME, "verficationCode"):
                    logger.info("→ 检测到验证码输入页面")
                    return True
                
                # 检查人机验证
                if self.page.find_elements(By.XPATH, "//span[contains(text(), '验证') or contains(text(), 'Verify')]"):
                    logger.info("→ 检测到人机验证页面")
                    return True
                
                self._random_wait(2, 3)
            except:
                pass
        return True

    def _handle_captcha(self) -> bool:
        """处理人机验证"""
        try:
            logger.info("步骤6: 处理人机验证")
            self._handle_retry_if_exists()
            
            # 检查是否直接进入了验证码页面
            if self.page.find_elements(By.NAME, "verficationCode"):
                logger.info("✓ 未触发人机验证，直接进入验证码页面")
                return True
            
            # 查找验证按钮
            try:
                verify_btn = WebDriverWait(self.page, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '验证') or contains(text(), 'Verify')]"))
                )
                logger.info("检测到人机验证，点击验证按钮")
                verify_btn.click()
                
                # 这里需要手动介入或对接打码平台
                logger.info("⚠️  请在浏览器中手动完成人机验证 (等待 300s)")
                WebDriverWait(self.page, 300).until_not(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '验证') or contains(text(), 'Verify')]"))
                )
                logger.info("✓ 验证已完成")
                return True
                
            except TimeoutException:
                logger.info("✓ 未检测到人机验证按钮")
                return True
                
        except Exception as e:
            logger.error(f"处理验证失败: {e}")
            return False

    def _input_email_code(self) -> bool:
        """输入邮箱验证码"""
        try:
            logger.info("步骤7: 输入邮箱验证码")
            
            # 等待输入框
            try:
                code_input = WebDriverWait(self.page, 30).until(
                    EC.presence_of_element_located((By.NAME, "verficationCode"))
                )
            except TimeoutException:
                logger.warning("未找到验证码输入框")
                return False
            
            # 获取验证码
            code = self.service.request_email_code(self.email)
            logger.info(f"获取到验证码: {code}")
            
            code_input.send_keys(code)
            self._random_wait(1, 2)
            
            # 点击下一步
            try:
                next_btn = self.page.find_element(By.XPATH, "//span[contains(text(), '下一步') or contains(text(), 'Next')]")
                next_btn.click()
                self._random_wait(2, 3)
                self._handle_retry_if_exists()
            except:
                logger.warning("点击下一步失败")
            
            return True
        except Exception as e:
            logger.error(f"输入验证码失败: {e}")
            return False

    def _set_password(self) -> bool:
        """设置密码"""
        try:
            logger.info("步骤8: 设置密码")
            try:
                pwd_input = WebDriverWait(self.page, 30).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                pwd_input.send_keys(self.password)
                self._random_wait(1, 2)
                
                next_btn = self.page.find_element(By.XPATH, "//span[contains(text(), '下一步') or contains(text(), 'Next')]")
                next_btn.click()
                self._random_wait(2, 3)
                self._handle_retry_if_exists()
                return True
            except TimeoutException:
                logger.warning("未找到密码输入框")
                return False
        except Exception as e:
            logger.error(f"设置密码失败: {e}")
            return False

    def _skip_profile_photo(self) -> bool:
        """跳过头像"""
        try:
            logger.info("步骤9: 跳过头像")
            try:
                skip_btn = WebDriverWait(self.page, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '暂时跳过') or contains(text(), 'Skip for now')]"))
                )
                skip_btn.click()
                self._random_wait(1, 2)
            except:
                pass
            return True
        except Exception as e:
            logger.warning(f"跳过头像失败: {e}")
            return True

    def _set_username(self) -> bool:
        """设置用户名"""
        try:
            logger.info("步骤10: 设置用户名")
            try:
                skip_btn = WebDriverWait(self.page, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '暂时跳过') or contains(text(), 'Skip for now')]"))
                )
                skip_btn.click()
                self._random_wait(1, 2)
                self.username = "AutoGenerated" # 暂时标记
            except:
                pass
            return True
        except Exception as e:
            logger.warning(f"设置用户名失败: {e}")
            return True

    def _skip_optional_steps(self) -> bool:
        """跳过可选步骤"""
        try:
            logger.info("步骤11: 跳过可选步骤")
            for _ in range(5):
                try:
                    skip_btn = self.page.find_element(By.XPATH, "//span[contains(text(), '暂时跳过') or contains(text(), 'Skip for now') or contains(text(), '下一步') or contains(text(), 'Next')]")
                    skip_btn.click()
                    self._random_wait(2, 3)
                except:
                    break
            return True
        except Exception as e:
            logger.warning(f"跳过可选步骤失败: {e}")
            return True

    def _handle_retry_if_exists(self):
        """处理重试按钮"""
        try:
            retry_btns = self.page.find_elements(By.XPATH, "//span[contains(text(), '重试') or contains(text(), 'Retry')]")
            if retry_btns:
                logger.info("⚠️  检测到重试按钮，点击重试")
                retry_btns[0].click()
                self._random_wait(2, 3)
        except:
            pass

    def _random_wait(self, min_sec: float = 1.0, max_sec: float = 3.0):
        time.sleep(random.uniform(min_sec, max_sec))

    def _generate_random_name(self):
        first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def _generate_random_birthday(self):
        year = random.randint(1990, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return year, month, day

    def _error_result(self, error_msg: str) -> Dict:
        logger.error(f"注册失败: {error_msg}")
        self.service.report_status('failed', error_msg, {'email': self.email})
        return {'success': False, 'error': error_msg}

    def close(self):
        """关闭浏览器"""
        if self.page:
            try:
                self.page.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")
