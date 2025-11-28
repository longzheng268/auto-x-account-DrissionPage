# -*- coding: utf-8 -*-
"""
Twitter/X 自动注册模块
基于 Playwright + Stealth 实现
"""
import logging
import random
import time
import msvcrt  # 用于Windows下的按键检测
from typing import Optional, Dict, List, Any
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser, Playwright, Locator, Error as PlaywrightError
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)


class TwitterRegister:
    """Twitter/X 自动注册器 - Playwright 实现"""
    
    def __init__(self, service, page: Optional[Page] = None, 
                 browser_path: Optional[str] = None, use_incognito: bool = False):
        """
        初始化注册器
        
        Args:
            service: 服务接口
            page: Playwright Page 对象（可选）
            browser_path: 浏览器路径（可选，自动检测）
            use_incognito: 是否使用无痕模式
        """
        self.service = service
        self.page = page
        self.browser_path = browser_path
        self.use_incognito = use_incognito
        
        # Playwright objects
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # 注册信息
        self.email = None
        self.password = None
        self.name = None
        self.birthday = None
        self.username = None
        
        logger.info("Twitter注册器已初始化（Playwright + Stealth实现）")
        logger.info("提示: 在终端运行期间按 'P' 键可暂停/恢复脚本执行")
    
    def _check_paused(self):
        """检查是否按下暂停键"""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key.lower() == b'p':
                logger.info("\n" + "="*40)
                logger.info("⏸️  脚本已暂停！")
                logger.info("按 'P' 键继续执行...")
                logger.info("="*40 + "\n")
                
                while True:
                    time.sleep(0.1)
                    if msvcrt.kbhit():
                        key = msvcrt.getch()
                        if key.lower() == b'p':
                            logger.info("▶️  脚本继续执行")
                            break
    
    def _ensure_page(self):
        """确保页面对象已创建"""
        if self.page is None:
            logger.info("=" * 60)
            logger.info("启动浏览器（Playwright - Stealth模式）")
            logger.info("=" * 60)
            
            self.playwright = sync_playwright().start()
            
            # 启动参数 - 最小化，避免触发风控
            # 移除所有危险参数：--disable-web-security, --disable-extensions 等
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
                "--lang=zh-CN",
            ]
            
            # 设置用户数据目录
            user_data_dir = Path(__file__).parent.parent / "browser_data"
            user_data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ 用户数据目录: {user_data_dir}")
            
            try:
                # 使用真实的窗口大小（常见分辨率）
                width = 800
                height = 600
                viewport = {'width': width, 'height': height}
                logger.info(f"✓ 视窗大小: {width}x{height}")
                
                # 使用真实稳定的 User-Agent（Chrome 120）
                ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                logger.info(f"✓ User-Agent: {ua[:50]}...")
                
                # 浏览器启动 - 使用 'chrome' 通道
                logger.info("✓ 启动 Chrome 浏览器 (channel='chrome')...")
                
                try:
                    if self.use_incognito:
                        # 无痕模式
                        logger.info("✓ 启用无痕模式")
                        self.browser = self.playwright.chromium.launch(
                            channel="chrome",
                            headless=False,
                            args=launch_args
                        )
                        self.context = self.browser.new_context(
                            viewport=viewport,
                            locale='zh-CN',
                            user_agent=ua,
                            timezone_id='Asia/Shanghai',
                            # 启用第三方 Cookie（Arkose 需要）
                            accept_downloads=True,
                            java_script_enabled=True,
                        )
                    else:
                        # 持久化模式 - 使用真实 profile
                        self.context = self.playwright.chromium.launch_persistent_context(
                            user_data_dir=str(user_data_dir),
                            channel="chrome",
                            headless=False,
                            args=launch_args,
                            viewport=viewport,
                            locale='zh-CN',
                            user_agent=ua,
                            timezone_id='Asia/Shanghai',
                            accept_downloads=True,
                            java_script_enabled=True,
                        )
                except Exception as e:
                    logger.warning(f"启动 Chrome 失败 ({e})，尝试使用默认 Chromium...")
                    # 回退到默认 Chromium
                    if self.use_incognito:
                        self.browser = self.playwright.chromium.launch(
                            headless=False,
                            args=launch_args
                        )
                        self.context = self.browser.new_context(
                            viewport=viewport,
                            locale='zh-CN',
                            user_agent=ua,
                            timezone_id='Asia/Shanghai',
                            accept_downloads=True,
                            java_script_enabled=True,
                        )
                    else:
                        self.context = self.playwright.chromium.launch_persistent_context(
                            user_data_dir=str(user_data_dir),
                            headless=False,
                            args=launch_args,
                            viewport=viewport,
                            locale='zh-CN',
                            user_agent=ua,
                            timezone_id='Asia/Shanghai',
                            accept_downloads=True,
                            java_script_enabled=True,
                        )
                
                # 获取或创建页面
                self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
                
                # === 应用 Stealth ===
                # 1. 使用 playwright-stealth 2.0.0
                stealth = Stealth()
                stealth.apply_stealth_sync(self.page)
                logger.info("✓ Stealth 插件已应用 (v2.0.0)")
                
                # 2. 注入完整的高级反检测脚本（早期注入，在文档创建前）
                self.page.add_init_script("""
(() => {
  try {
    // 1. webdriver - 最重要
    Object.defineProperty(navigator, 'webdriver', { 
      get: () => undefined, 
      configurable: true 
    });
  } catch (e) {}

  try {
    // 2. languages - 真实语言列表
    Object.defineProperty(navigator, 'languages', { 
      get: () => ['zh-CN', 'zh', 'en-US', 'en'], 
      configurable: true 
    });
  } catch (e) {}

  try {
    // 3. plugins/mimeTypes - 模拟真实插件（带 item/namedItem）
    const fakePlugins = [
      { 
        name: 'Chrome PDF Plugin', 
        filename: 'internal-pdf-viewer', 
        description: 'Portable Document Format',
        length: 1
      },
      {
        name: 'Chrome PDF Viewer',
        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
        description: '',
        length: 1
      }
    ];
    
    const pluginArray = {
      length: fakePlugins.length,
      item: function(index) {
        return this[index] || null;
      },
      namedItem: function(name) {
        return fakePlugins.find(p => p.name === name) || null;
      },
      refresh: function() {}
    };
    
    fakePlugins.forEach((plugin, index) => {
      pluginArray[index] = plugin;
    });
    
    Object.setPrototypeOf(pluginArray, PluginArray.prototype);
    Object.defineProperty(navigator, 'plugins', { 
      get: () => pluginArray, 
      configurable: true 
    });
    
    // mimeTypes
    const mimeTypesArray = {
      length: 0,
      item: () => null,
      namedItem: () => null
    };
    Object.setPrototypeOf(mimeTypesArray, MimeTypeArray.prototype);
    Object.defineProperty(navigator, 'mimeTypes', { 
      get: () => mimeTypesArray, 
      configurable: true 
    });
  } catch (e) {}

  try {
    // 4. permissions.query - 绑定原函数
    const originalQuery = navigator.permissions && navigator.permissions.query;
    if (originalQuery) {
      navigator.permissions.query = function(parameters) {
        if (parameters && parameters.name === 'notifications') {
          return Promise.resolve({ state: Notification.permission });
        }
        return originalQuery.call(this, parameters);
      };
    }
  } catch (e) {}

  try {
    // 5. window.chrome - 必须存在
    if (!window.chrome) {
      window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
      };
    }
  } catch (e) {}

  try {
    // 6. hardwareConcurrency - 真实值
    Object.defineProperty(navigator, 'hardwareConcurrency', {
      get: () => 8,
      configurable: true
    });
  } catch (e) {}

  try {
    // 7. deviceMemory - 真实值
    Object.defineProperty(navigator, 'deviceMemory', {
      get: () => 8,
      configurable: true
    });
  } catch (e) {}

  try {
    // 8. WebGL - 模拟真实显卡
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
      // UNMASKED_VENDOR_WEBGL
      if (parameter === 37445) {
        return 'Intel Inc.';
      }
      // UNMASKED_RENDERER_WEBGL
      if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
      }
      return getParameter.call(this, parameter);
    };
  } catch (e) {}

  try {
    // 9. platform - 保持一致
    Object.defineProperty(navigator, 'platform', {
      get: () => 'Win32',
      configurable: true
    });
  } catch (e) {}

  try {
    // 10. maxTouchPoints - 桌面设备
    Object.defineProperty(navigator, 'maxTouchPoints', {
      get: () => 0,
      configurable: true
    });
  } catch (e) {}
})();
                """)
                logger.info("✓ 完整反检测脚本已注入（支持 Arkose）")
                
                logger.info("✓ 浏览器启动成功")
                logger.info("")
                
            except Exception as e:
                logger.error("=" * 60)
                logger.error(f"✗ 浏览器启动失败！")
                logger.error(f"错误详情: {e}")
                logger.error("=" * 60)
                raise
    
    def _get_random_ua(self):
        ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(ua_list)
    
    def register(self) -> Dict:
        """
        执行完整的注册流程
        """
        try:
            self._ensure_page()
            
            logger.info("=" * 60)
            logger.info("开始 Twitter/X 注册流程")
            logger.info("=" * 60)
            
            # 上报状态：注册开始
            self.service.report_status('started', '注册流程启动')
            
            # 步骤1: 直接访问注册页面
            self.service.report_status('visit_page', '正在访问注册页面')
            if not self._visit_signup_page():
                return self._error_result("访问注册页面失败")
            
            # 步骤2: 点击创建账号
            if not self._click_create_account():
                return self._error_result("点击创建账号失败")
            
            # 步骤3: 切换到邮箱注册
            if not self._switch_to_email_signup():
                return self._error_result("切换邮箱注册失败")
            
            # 步骤4: 获取邮箱和密码
            logger.info("步骤4: 准备获取邮箱和密码...")
            self.service.report_status('need_email', '准备获取邮箱和密码')
            self._random_wait(0.5, 1)
            
            self.email, self.password = self.service.request_email()
            logger.info(f"获取到邮箱: {self.email}")
            
            # 步骤5: 填写注册表单
            self.service.report_status('filling_form', '正在填写注册表单', {
                'email': self.email,
                'name': self.name if hasattr(self, 'name') and self.name else None
            })
            if not self._fill_signup_form():
                return self._error_result("填写注册表单失败")
            
            # 步骤6: 处理人机验证
            self.service.report_status('need_captcha', '需要人机验证', {
                'page_url': self.page.url if self.page else None
            })
            if not self._handle_captcha():
                return self._error_result("处理人机验证失败")
            
            # 步骤7: 输入邮箱验证码
            logger.info("步骤7: 准备输入邮箱验证码...")
            self.service.report_status('need_email_code', '准备输入验证码', {
                'email': self.email
            })
            self._random_wait(0.5, 1)
            
            if not self._input_email_code():
                return self._error_result("输入邮箱验证码失败")
            
            # 步骤8: 设置密码
            self.service.report_status('setting_password', '正在设置密码')
            if not self._set_password():
                return self._error_result("设置密码失败")
            
            # 步骤9: 跳过头像
            if not self._skip_profile_photo():
                return self._error_result("跳过头像失败")
            
            # 步骤10: 设置用户名
            self.service.report_status('setting_username', '正在设置用户名')
            if not self._set_username():
                return self._error_result("设置用户名失败")
            
            # 步骤11: 跳过可选步骤
            if not self._skip_optional_steps():
                return self._error_result("跳过可选步骤失败")
            
            logger.info("=" * 60)
            logger.info("✓ Twitter/X 注册成功！")
            logger.info(f"邮箱: {self.email}")
            logger.info(f"用户名: {self.username}")
            logger.info("=" * 60)
            
            # 上报状态：注册完成
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
    
    def _error_result(self, error_msg: str) -> Dict:
        """返回错误结果"""
        logger.error(f"注册失败: {error_msg}")
        
        # 上报状态：注册失败
        self.service.report_status('failed', error_msg, {
            'email': self.email,
            'username': self.username
        })
        
        return {
            'success': False,
            'error': error_msg,
            'email': self.email,
            'password': self.password,
            'username': self.username
        }
    
    def _random_wait(self, min_seconds=1.0, max_seconds=3.0):
        """随机等待"""
        self._check_paused()  # 检查暂停
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)
        self._check_paused()  # 再次检查
    
    def _find_element(self, selector: str, timeout: float = 1.0) -> Optional[Locator]:
        """
        查找元素辅助方法，模拟 DrissionPage 的查找逻辑
        selector 支持:
        - text:文本内容 -> text=文本内容
        - tag:input@name=xxx -> input[name='xxx']
        - @id=xxx -> #xxx
        """
        try:
            # 转换选择器
            playwright_selector = selector
            if selector.startswith('text:'):
                text = selector.split(':', 1)[1]
                playwright_selector = f"text={text}"
            elif selector.startswith('tag:'):
                # 简单处理 tag:input@name=value -> input[name='value']
                # tag:input@autocomplete=one-time-code -> input[autocomplete='one-time-code']
                parts = selector.split('@')
                tag = parts[0].split(':')[1]
                if len(parts) > 1:
                    attr_part = parts[1]
                    if '=' in attr_part:
                        attr, val = attr_part.split('=', 1)
                        playwright_selector = f"{tag}[{attr}='{val}']"
                    else:
                        playwright_selector = f"{tag}[{attr_part}]"
                else:
                    playwright_selector = tag
            elif selector.startswith('@id='):
                playwright_selector = f"#{selector.split('=', 1)[1]}"
            
            # 查找
            locator = self.page.locator(playwright_selector).first
            try:
                locator.wait_for(state='attached', timeout=timeout * 1000)
                return locator
            except:
                return None
                
        except Exception as e:
            # logger.debug(f"查找元素失败 {selector}: {e}")
            return None

    def _find_elements(self, selector: str, timeout: float = 1.0) -> List[Locator]:
        """查找多个元素"""
        try:
            # 转换选择器 (简化版，同上)
            playwright_selector = selector
            if selector.startswith('tag:'):
                playwright_selector = selector.split(':')[1]
            
            locator = self.page.locator(playwright_selector)
            try:
                # 等待至少一个出现
                locator.first.wait_for(state='attached', timeout=timeout * 1000)
            except:
                pass
            
            return locator.all()
        except:
            return []

    def _handle_retry_if_exists(self, max_retries=3) -> bool:
        """处理重试按钮"""
        try:
            for attempt in range(max_retries):
                retry_btn = self._find_element('text:重试', timeout=2)
                if not retry_btn:
                    retry_btn = self._find_element('text:Retry', timeout=1)
                if not retry_btn:
                    retry_btn = self._find_element('text:重新尝试', timeout=1)
                if not retry_btn:
                    retry_btn = self._find_element('text:Try again', timeout=1)
                
                if retry_btn and retry_btn.is_visible():
                    logger.info(f"⚠️  检测到重试按钮，点击重试 (第{attempt+1}次)")
                    retry_btn.click()
                    self._random_wait(2, 3)
                else:
                    if attempt > 0:
                        logger.info("✓ 重试按钮已消失")
                    return True
            
            return True
            
        except Exception as e:
            logger.debug(f"检查重试按钮时出错: {e}")
            return True
    
    def _visit_signup_page(self) -> bool:
        """访问注册页面"""
        try:
            logger.info("步骤1: 访问注册页面")
            self.page.goto('https://x.com/i/flow/signup', timeout=60000)
            
            logger.info("等待页面加载...")
            self._random_wait(2, 4)
            
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
            
            # 查找所有按钮
            buttons = self.page.locator("button").all()
            logger.info(f"找到 {len(buttons)} 个 button 元素")
            
            for i, btn in enumerate(buttons):
                try:
                    text = btn.inner_text()
                    # logger.info(f"  Button[{i}]: '{text}'")
                    
                    if text and ('创建账号' in text or 'Create account' in text or 
                                 '创建帐号' in text or 'Sign up' in text):
                        logger.info(f"找到目标按钮[{i}]: '{text}'")
                        
                        btn.scroll_into_view_if_needed()
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
            
            email_link = self._find_element('text:改用电子邮件', timeout=5)
            if not email_link:
                email_link = self._find_element('text:Use email instead', timeout=2)
            
            if email_link:
                email_link.click()
                logger.info("✓ 已切换到邮箱注册")
                self._random_wait(1, 2)
                return True
            
            logger.info("可能已经是邮箱注册模式")
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
            logger.info(f"生日: {self.birthday}")
            
            # 填写姓名
            name_input = self._find_element('tag:input@name=name', timeout=10)
            if name_input:
                logger.info("填写姓名...")
                name_input.fill(self.name)
                self._random_wait(0.5, 1)
            else:
                logger.warning("未找到姓名输入框")
            
            # 填写邮箱
            email_input = self._find_element('tag:input@type=email', timeout=5)
            if email_input:
                logger.info("填写邮箱...")
                email_input.fill(self.email)
                self._random_wait(0.5, 1)
            else:
                logger.warning("未找到邮箱输入框")
            
            # 填写生日
            self._fill_birthday()
            
            # 点击下一步
            next_btn = self._find_element('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self._find_element('text:Next', timeout=2)
            
            if next_btn:
                next_btn.click()
                logger.info("✓ 表单已提交，等待页面响应...")
                self._random_wait(3, 5)
                self._handle_retry_if_exists()
                
                # 检测页面状态
                logger.info("检测页面状态...")
                for attempt in range(15):
                    verify_btn = self._find_element('text:验证', timeout=1)
                    if not verify_btn:
                        verify_btn = self._find_element('text:Verify', timeout=1)
                    
                    code_input = self._find_element('tag:input@autocomplete=one-time-code', timeout=1)
                    pwd_input = self._find_element('tag:input@type=password', timeout=1)
                    
                    error_msg = self._find_element('text:出错', timeout=1)
                    if not error_msg: error_msg = self._find_element('text:error', timeout=1)
                    if not error_msg: error_msg = self._find_element('text:错误', timeout=1)
                    
                    if verify_btn:
                        logger.info("→ 检测到人机验证页面")
                        break
                    elif code_input:
                        logger.info("→ 检测到验证码输入页面")
                        break
                    elif pwd_input:
                        logger.info("→ 检测到密码设置页面")
                        break
                    elif error_msg:
                        try:
                            error_text = error_msg.inner_text()
                            logger.warning(f"→ 检测到错误: {error_text}")
                            if '阻止' in error_text or 'blocked' in error_text.lower():
                                logger.error("⚠️  可能被X检测并阻止了")
                        except:
                            pass
                        break
                    else:
                        self._random_wait(2, 3)
                
                logger.info("✓ 表单填写完成")
            
            return True
            
        except Exception as e:
            logger.error(f"填写表单失败: {e}")
            return False
    
    def _fill_birthday(self):
        """填写生日"""
        try:
            year, month, day = self.birthday
            logger.info(f"填写生日: {year}-{month:02d}-{day:02d}")
            
            all_selects = self.page.locator("select").all()
            logger.info(f"找到 {len(all_selects)} 个下拉框")
            
            for i, select_ele in enumerate(all_selects):
                try:
                    select_id = select_ele.get_attribute('id') or ''
                    select_labelledby = select_ele.get_attribute('aria-labelledby') or ''
                    
                    label_text = ''
                    if select_labelledby:
                        label_ele = self.page.locator(f"#{select_labelledby}").first
                        if label_ele.count() > 0:
                            label_text = label_ele.inner_text().lower()
                    
                    value_to_select = None
                    field_name = ''
                    
                    if ('month' in label_text or '月' in label_text or select_id == 'SELECTOR_1'):
                        value_to_select = str(month)
                        field_name = '月份'
                    elif ('day' in label_text or '日' in label_text or select_id == 'SELECTOR_2'):
                        value_to_select = str(day)
                        field_name = '日期'
                    elif ('year' in label_text or '年' in label_text or select_id == 'SELECTOR_3'):
                        value_to_select = str(year)
                        field_name = '年份'
                    
                    if value_to_select:
                        logger.info(f"  → 选择{field_name}: {value_to_select}")
                        select_ele.select_option(value=value_to_select)
                        self._random_wait(0.5, 1)
                except Exception as e:
                    logger.warning(f"  ✗ 选择{field_name}失败: {e}")
            
            logger.info("✓ 生日填写完成")
            
        except Exception as e:
            logger.warning(f"填写生日失败: {e}")

    def _handle_captcha(self) -> bool:
        """处理人机验证"""
        try:
            logger.info("步骤6: 处理人机验证")
            self._handle_retry_if_exists()
            
            code_input = self._find_element('tag:input@autocomplete=one-time-code', timeout=2)
            if code_input:
                logger.info("✓ 未触发人机验证，直接进入验证码页面")
                return True
            
            verify_btn = self._find_element('text:验证', timeout=3)
            if not verify_btn:
                verify_btn = self._find_element('text:Verify', timeout=1)
            
            if not verify_btn:
                code_input = self._find_element('tag:input@autocomplete=one-time-code', timeout=2)
                if code_input:
                    logger.info("✓ 检测到验证码输入框，跳过验证")
                    return True
                logger.info("✓ 未检测到人机验证按钮")
                return True
            
            logger.info("检测到人机验证，点击验证按钮")
            verify_btn.click()
            self._random_wait(2, 3)
            
            # 请求验证解决方案
            captcha_info = self.service.request_captcha_solution(
                captcha_type='funcaptcha',
                site_key='',
                page_url=self.page.url
            )
            
            if captcha_info.get('method') == 'manual':
                logger.info("=" * 60)
                logger.info("⚠️  请在浏览器中手动完成人机验证")
                logger.info("等待最多 300 秒...")
                logger.info("=" * 60)
                
                start_time = time.time()
                while time.time() - start_time < 300:
                    verify_btn = self._find_element('text:验证', timeout=1)
                    if not verify_btn:
                        verify_btn = self._find_element('text:Verify', timeout=1)
                    
                    if not verify_btn:
                        logger.info("✓ 验证已完成")
                        break
                    time.sleep(3)
            
            self._random_wait(2, 3)
            return True
            
        except Exception as e:
            logger.error(f"处理验证失败: {e}")
            return False

    def _input_email_code(self) -> bool:
        """输入邮箱验证码"""
        try:
            logger.info("步骤7: 输入邮箱验证码")
            
            code_input = None
            for attempt in range(5):
                code_input = self._find_element('tag:input@autocomplete=one-time-code', timeout=10)
                if code_input:
                    logger.info(f"✓ 找到验证码输入框")
                    break
                
                code_input = self._find_element('tag:input@name=verficationCode', timeout=5)
                if code_input:
                    logger.info(f"✓ 找到验证码输入框（备用方式）")
                    break
                
                logger.info(f"  未找到验证码输入框，重试... ({attempt+1}/5)")
                self._random_wait(2, 3)
            
            if not code_input:
                logger.warning("未找到验证码输入框")
                return True
            
            code = self.service.request_email_code(self.email)
            logger.info(f"获取到验证码: {code}")
            
            code_input.fill(code)
            self._random_wait(1, 2)
            
            next_btn = self._find_element('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self._find_element('text:Next', timeout=2)
            
            if next_btn:
                next_btn.click()
                self._random_wait(2, 3)
                self._handle_retry_if_exists()
            
            return True
            
        except Exception as e:
            logger.error(f"输入验证码失败: {e}")
            return False

    def _set_password(self) -> bool:
        """设置密码"""
        try:
            logger.info("步骤8: 设置密码")
            
            pwd_input = self._find_element('tag:input@type=password', timeout=30)
            if not pwd_input:
                logger.warning("未找到密码输入框")
                return True
            
            pwd_input.fill(self.password)
            self._random_wait(1, 2)
            
            next_btn = self._find_element('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self._find_element('text:Next', timeout=2)
            
            if next_btn:
                next_btn.click()
                self._random_wait(2, 3)
                self._handle_retry_if_exists()
            
            return True
            
        except Exception as e:
            logger.error(f"设置密码失败: {e}")
            return False

    def _skip_profile_photo(self) -> bool:
        """跳过头像上传"""
        try:
            logger.info("步骤9: 跳过头像上传")
            
            skip_btn = self._find_element('text:Skip for now', timeout=10)
            if not skip_btn:
                skip_btn = self._find_element('text:跳过', timeout=2)
            
            if skip_btn:
                skip_btn.click()
                self._random_wait(1, 2)
            
            return True
            
        except Exception as e:
            logger.warning(f"跳过头像失败: {e}")
            return True

    def _set_username(self) -> bool:
        """设置用户名"""
        try:
            logger.info("步骤10: 设置用户名")
            
            username_input = self._find_element('tag:input@autocomplete=username', timeout=30)
            if not username_input:
                logger.warning("未找到用户名输入框")
                return False
            
            for attempt in range(10):
                self.username = self._generate_username(self.name)
                logger.info(f"尝试用户名: {self.username}")
                
                username_input.fill("")
                username_input.fill(self.username)
                self._random_wait(1, 2)
                
                error = self._find_element('text:已被使用', timeout=2)
                if not error:
                    error = self._find_element('text:isn\'t available', timeout=1)
                
                if not error:
                    logger.info(f"✓ 用户名可用: {self.username}")
                    break
                    
                logger.warning(f"用户名已被使用: {self.username}")
            
            next_btn = self._find_element('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self._find_element('text:Next', timeout=2)
            if not next_btn:
                next_btn = self._find_element('text:注册', timeout=2)
            
            if next_btn:
                next_btn.click()
                self._random_wait(2, 3)
                self._handle_retry_if_exists()
            
            return True
            
        except Exception as e:
            logger.error(f"设置用户名失败: {e}")
            return False

    def _skip_optional_steps(self) -> bool:
        """跳过可选步骤"""
        try:
            logger.info("步骤11: 跳过可选步骤")
            
            for i in range(5):
                self._random_wait(1, 2)
                
                skip_btn = self._find_element('text:Skip', timeout=3)
                if not skip_btn:
                    skip_btn = self._find_element('text:跳过', timeout=1)
                if not skip_btn:
                    skip_btn = self._find_element('text:Not now', timeout=1)
                if not skip_btn:
                    skip_btn = self._find_element('text:Next', timeout=1)
                
                if skip_btn:
                    skip_btn.click()
                    logger.info(f"跳过步骤 {i+1}")
                    self._random_wait(1, 2)
                else:
                    logger.info("没有更多跳过按钮")
                    break
            
            return True
            
        except Exception as e:
            logger.warning(f"跳过可选步骤失败: {e}")
            return False

    def _generate_random_name(self) -> str:
        """生成随机名字"""
        first_names = ["Alex", "Sam", "Jordan", "Taylor", "Morgan"]
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Miller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_random_birthday(self) -> tuple:
        """生成随机生日（18-35岁）"""
        from datetime import datetime
        today = datetime.now()
        age = random.randint(18, 35)
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        
        if birth_month in [1, 3, 5, 7, 8, 10, 12]:
            max_day = 31
        elif birth_month in [4, 6, 9, 11]:
            max_day = 30
        else:
            if (birth_year % 4 == 0 and birth_year % 100 != 0) or (birth_year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        
        birth_day = random.randint(1, max_day)
        return (birth_year, birth_month, birth_day)
    
    def _generate_username(self, base: str, max_length: int = 15) -> str:
        """生成用户名"""
        base = ''.join(c for c in base if c.isalnum())
        username = base.lower()
        username += str(random.randint(100, 9999))
        return username[:max_length]
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("浏览器已关闭")
        except:
            pass
