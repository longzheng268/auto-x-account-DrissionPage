# -*- coding: utf-8 -*-
"""
Twitter/X 自动注册模块
100% 基于 DrissionPage 原生功能，不造轮子
"""
import logging
import random
import time
from typing import Optional, Dict
from pathlib import Path

from DrissionPage import ChromiumPage, ChromiumOptions

logger = logging.getLogger(__name__)


class TwitterRegister:
    """Twitter/X 自动注册器 - 纯 DrissionPage 实现"""
    
    def __init__(self, service, page: Optional[ChromiumPage] = None, 
                 browser_path: Optional[str] = None, use_incognito: bool = False):
        """
        初始化注册器
        
        Args:
            service: 服务接口
            page: DrissionPage 页面对象（可选）
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
        
        logger.info("Twitter注册器已初始化（纯DrissionPage实现）")
    
    def _ensure_page(self):
        """确保页面对象已创建 - 完全使用 DrissionPage 自动管理"""
        if self.page is None:
            logger.info("=" * 60)
            logger.info("启动浏览器（DrissionPage自动管理 - 增强隐匿模式）")
            logger.info("=" * 60)
            
            # 配置 ChromiumOptions - 完全使用 DrissionPage 功能
            options = ChromiumOptions(read_file=False)
            
            # 设置浏览器路径
            if self.browser_path:
                options.set_browser_path(self.browser_path)
                logger.info(f"✓ 使用指定浏览器: {self.browser_path}")
            else:
                # 尝试项目内置浏览器
                project_dir = Path(__file__).parent.parent
                project_chrome = project_dir / "twitter_auto_register" / "chrome-win" / "chrome.exe"
                
                if project_chrome.exists():
                    options.set_browser_path(str(project_chrome))
                    logger.info(f"✓ 找到项目内置 Chromium")
                    logger.info(f"   路径: {project_chrome}")
                else:
                    logger.info("⚠ 项目内置浏览器不存在，使用系统浏览器")
                    logger.info(f"   查找路径: {project_chrome}")
            
            # 设置用户数据目录
            user_data_dir = Path(__file__).parent.parent / "browser_data"
            user_data_dir.mkdir(parents=True, exist_ok=True)
            options.set_user_data_path(str(user_data_dir))
            logger.info(f"✓ 用户数据目录: {user_data_dir}")
            
            # 自动分配端口
            options.auto_port()
            logger.info("✓ 自动分配调试端口")
            
            # 无痕模式
            if self.use_incognito:
                options.incognito()
                logger.info("✓ 启用无痕模式")
            
            # === 增强反检测配置 ===
            logger.info("配置浏览器参数 (增强隐匿)...")
            
            # 1. 随机 User-Agent
            ua_list = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]
            ua = random.choice(ua_list)
            options.set_user_agent(ua)
            logger.info(f"✓ User-Agent: {ua[:50]}...")
            
            # 2. 启动参数
            options.set_argument('--no-first-run')
            options.set_argument('--no-default-browser-check')
            options.set_argument('--disable-popup-blocking')
            options.set_argument('--disable-extensions')
            options.set_argument('--disable-dev-shm-usage')
            options.set_argument('--disable-web-security')
            options.set_argument('--disable-blink-features=AutomationControlled')
            options.set_argument('--lang=zh-CN')
            
            options.set_load_mode('normal')
            logger.info("✓ 浏览器配置完成")
            
            # 创建页面
            try:
                logger.info("")
                logger.info("正在启动浏览器...")
                self.page = ChromiumPage(options)
                
                # === 配置隐匿模式 ===
                # 1. 动态视窗
                width = random.randint(1024, 1920)
                height = random.randint(768, 1080)
                self.page.set.window.size(width, height)
                logger.info(f"✓ 动态视窗: {width}x{height}")
                
                # 2. 注入反检测脚本
                stealth_js = """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined, configurable: true});
                    delete Object.getPrototypeOf(navigator).webdriver;
                    Object.defineProperty(Object.getPrototypeOf(navigator), 'webdriver', {get: () => undefined, configurable: true});
                    
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                    );
                    
                    Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en'], configurable: true});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5], configurable: true});
                    Object.defineProperty(navigator, 'mimeTypes', {get: () => [1, 2, 3, 4, 5], configurable: true});
                    Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8, configurable: true});
                    Object.defineProperty(navigator, 'deviceMemory', {get: () => 8, configurable: true});
                    Object.defineProperty(navigator, 'platform', {get: () => 'Win32', configurable: true});
                    
                    window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};
                    
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) return 'Intel Inc.';
                        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                        return getParameter.call(this, parameter);
                    };
                """
                
                self.page.run_cdp('Page.addScriptToEvaluateOnNewDocument', source=stealth_js)
                logger.info("✓ CDP反检测脚本: 已注入 (含原型链)")
                
                # 3. 网络层请求头
                logger.info("")
            except Exception as e:
                logger.error("")
                logger.error("=" * 60)
                logger.error(f"✗ 浏览器启动失败！")
                logger.error("可能的原因：")
                logger.error("1. 未安装 Chrome/Chromium/Edge 浏览器")
                logger.error("2. 项目内置浏览器路径不正确")
                logger.error("3. 浏览器被占用或端口冲突")
                logger.error("")
                logger.error(f"错误详情: {e}")
                logger.error("=" * 60)
                raise
    
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
            self._random_wait(0.5, 1)  # 给外部服务一点反应时间
            
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
            self._random_wait(0.5, 1)  # 给外部服务一点反应时间
            
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
    
    def _random_wait(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机等待 - 使用 time.sleep"""
        wait_time = random.uniform(min_sec, max_sec)
        time.sleep(wait_time)
    
    def _handle_retry_if_exists(self, max_retries=3) -> bool:
        """处理重试按钮 - 纯 DrissionPage"""
        try:
            for attempt in range(max_retries):
                # 使用 DrissionPage 查找重试按钮
                retry_btn = self.page.ele('text:重试', timeout=2)
                if not retry_btn:
                    retry_btn = self.page.ele('text:Retry', timeout=1)
                if not retry_btn:
                    retry_btn = self.page.ele('text:重新尝试', timeout=1)
                if not retry_btn:
                    retry_btn = self.page.ele('text:Try again', timeout=1)
                
                if retry_btn:
                    logger.info(f"⚠️  检测到重试按钮，点击重试 (第{attempt+1}次)")
                    retry_btn.click()
                    self._random_wait(2, 3)
                else:
                    # 没有重试按钮，正常
                    if attempt == 0:
                        logger.debug("未检测到重试按钮")
                    else:
                        logger.info("✓ 重试按钮已消失")
                    return True
            
            # 达到最大重试次数，检查是否还有重试按钮
            retry_btn = self.page.ele('text:重试', timeout=1)
            if retry_btn:
                logger.warning(f"⚠️  重试了{max_retries}次，但重试按钮仍存在")
            
            return True
            
        except Exception as e:
            logger.debug(f"检查重试按钮时出错: {e}")
            return True  # 继续执行
    
    def _visit_signup_page(self) -> bool:
        """访问注册页面"""
        try:
            logger.info("步骤1: 访问注册页面")
            self.page.get('https://x.com/i/flow/signup')
            
            # 使用 DrissionPage 等待页面加载完成
            logger.info("等待页面加载...")
            self._random_wait(2, 4)
            
            # 再次注入反检测代码（每个页面都需要）
            self.page.run_js('''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            ''')
            
            # 检查是否有重试按钮
            self._handle_retry_if_exists()
            
            logger.info("✓ 注册页面访问成功")
            return True
        except Exception as e:
            logger.error(f"访问注册页面失败: {e}")
            return False
    
    def _click_create_account(self) -> bool:
        """点击创建账号按钮 - 纯 DrissionPage 实现"""
        try:
            logger.info("步骤2: 点击创建账号按钮")
            
            # 等待页面加载
            self._random_wait(2, 3)
            
            # 检查是否有重试按钮
            self._handle_retry_if_exists()
            
            # 方法：遍历所有button（已验证最可靠）
            # 减少timeout，提高查找速度
            all_buttons = self.page.eles('tag:button', timeout=3)
            logger.info(f"找到 {len(all_buttons)} 个 button 元素")
            
            # 先打印所有按钮文本，方便调试
            for i, btn in enumerate(all_buttons):
                text = btn.text
                logger.info(f"  Button[{i}]: '{text}'")
            
            for i, btn in enumerate(all_buttons):
                text = btn.text
                if text and ('创建账号' in text or 'Create account' in text or 
                             '创建帐号' in text or 'Sign up' in text):
                    logger.info(f"找到目标按钮[{i}]: '{text}'")
                    
                    # 滚动到可见区域（DrissionPage 自动功能）
                    btn.scroll.to_see()
                    self._random_wait(0.5, 1)
                    
                    # 点击（DrissionPage 自动处理）
                    btn.click()
                    logger.info("✓ 点击成功")
                    self._random_wait(2, 4)
                    
                    # 点击后也可能出现重试
                    self._handle_retry_if_exists()
                    
                    return True
            
            logger.warning("未找到创建账号按钮")
            return False
            
        except Exception as e:
            logger.error(f"点击创建账号失败: {e}")
            return False
    
    def _switch_to_email_signup(self) -> bool:
        """切换到邮箱注册"""
        try:
            logger.info("步骤3: 切换到邮箱注册")
            
            # 使用 DrissionPage 的文本定位
            email_link = self.page.ele('text:改用电子邮件', timeout=5)
            if not email_link:
                email_link = self.page.ele('text:Use email instead', timeout=2)
            
            if email_link:
                email_link.click()
                logger.info("✓ 已切换到邮箱注册")
                self._random_wait(1, 2)
                return True
            
            logger.info("可能已经是邮箱注册模式")
            return True
            
        except Exception as e:
            logger.warning(f"切换邮箱注册失败: {e}")
            return True  # 继续尝试
    
    def _fill_signup_form(self) -> bool:
        """填写注册表单 - 纯 DrissionPage"""
        try:
            logger.info("步骤5: 填写注册表单")
            
            # 生成信息
            self.name = self._generate_random_name()
            self.birthday = self._generate_random_birthday()
            
            logger.info(f"姓名: {self.name}")
            logger.info(f"邮箱: {self.email}")
            logger.info(f"生日: {self.birthday}")
            
            # 填写姓名 - 使用 DrissionPage 定位
            name_input = self.page.ele('tag:input@name=name', timeout=10)
            if name_input:
                logger.info("填写姓名...")
                name_input.input(self.name)
                self._random_wait(0.5, 1)
            else:
                logger.warning("未找到姓名输入框")
            
            # 填写邮箱
            email_input = self.page.ele('tag:input@type=email', timeout=5)
            if email_input:
                logger.info("填写邮箱...")
                email_input.input(self.email)
                self._random_wait(0.5, 1)
            else:
                logger.warning("未找到邮箱输入框")
            
            # 填写生日
            self._fill_birthday()
            
            # 点击下一步 - DrissionPage 文本定位
            next_btn = self.page.ele('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self.page.ele('text:Next', timeout=2)
            
            if next_btn:
                next_btn.click()
                logger.info("✓ 表单已提交，等待页面响应...")
                
                # 等待页面跳转或加载（DrissionPage 等待）
                self._random_wait(3, 5)
                
                # 点击后可能出现重试
                self._handle_retry_if_exists()
                
                # 使用 DrissionPage 等待多种可能的页面状态
                logger.info("检测页面状态...")
                for attempt in range(15):  # 最多等待45秒
                    # 每次检测前注入反检测代码
                    try:
                        self.page.run_js('Object.defineProperty(navigator, "webdriver", {get: () => undefined});')
                    except:
                        pass
                    
                    # 检查是否出现了验证按钮
                    verify_btn = self.page.ele('text:验证', timeout=1)
                    if not verify_btn:
                        verify_btn = self.page.ele('text:Verify', timeout=1)
                    
                    # 检查是否出现了验证码输入框
                    code_input = self.page.ele('tag:input@autocomplete=one-time-code', timeout=1)
                    
                    # 检查是否出现了密码输入框
                    pwd_input = self.page.ele('tag:input@type=password', timeout=1)
                    
                    # 检查是否有错误提示（更全面）
                    error_msg = self.page.ele('text:出错', timeout=1)
                    if not error_msg:
                        error_msg = self.page.ele('text:error', timeout=1)
                    if not error_msg:
                        error_msg = self.page.ele('text:错误', timeout=1)
                    if not error_msg:
                        error_msg = self.page.ele('text:Something went wrong', timeout=1)
                    
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
                        error_text = error_msg.text if error_msg else ""
                        logger.warning(f"→ 检测到错误: {error_text}")
                        # 检查是否被阻止
                        if '阻止' in error_text or 'blocked' in error_text.lower():
                            logger.error("⚠️  可能被X检测并阻止了")
                            logger.error("建议: 1. 关闭浏览器重新尝试 2. 更换网络环境")
                        break
                    else:
                        # 使用 DrissionPage 检查页面状态
                        try:
                            current_url = self.page.url
                            page_title = self.page.title
                            logger.info(f"  等待... ({attempt+1}/15)")
                            logger.info(f"    URL: {current_url[:80]}")
                            logger.info(f"    标题: {page_title[:40] if page_title else 'None'}")
                        except Exception as e:
                            logger.warning(f"  无法获取页面信息: {e}")
                        self._random_wait(2, 3)
                
                logger.info("✓ 表单填写完成")
            
            return True
            
        except Exception as e:
            logger.error(f"填写表单失败: {e}")
            return False
    
    def _fill_birthday(self):
        """填写生日 - 纯 DrissionPage"""
        try:
            year, month, day = self.birthday
            logger.info(f"填写生日: {year}-{month:02d}-{day:02d}")
            
            # 使用 DrissionPage 查找所有 select 元素
            all_selects = self.page.eles('tag:select', timeout=5)
            logger.info(f"找到 {len(all_selects)} 个下拉框")
            
            for i, select_ele in enumerate(all_selects):
                # 获取select的属性
                select_id = select_ele.attr('id') or ''
                select_labelledby = select_ele.attr('aria-labelledby') or ''
                
                logger.info(f"下拉框[{i}]: id={select_id}, aria-labelledby={select_labelledby}")
                
                # 通过 aria-labelledby 找到对应的 label 元素并读取文本
                label_text = ''
                if select_labelledby:
                    # 使用 DrissionPage 通过 id 查找 label
                    label_ele = self.page.ele(f'@id={select_labelledby}', timeout=2)
                    if label_ele:
                        label_text = label_ele.text.lower()
                        logger.info(f"  标签文本: '{label_text}'")
                
                # 根据 label 文本或 id 判断是月/日/年
                # Twitter 的顺序: SELECTOR_1=月, SELECTOR_2=日, SELECTOR_3=年
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
                    
                    # 使用 DrissionPage 的 select 功能
                    try:
                        select_ele.select.by_value(value_to_select)
                        self._random_wait(0.5, 1)
                        
                        # 验证选择是否成功
                        selected_value = select_ele.attr('value') or select_ele.value
                        if selected_value == value_to_select:
                            logger.info(f"  ✓ {field_name}选择成功: {selected_value}")
                        else:
                            logger.warning(f"  ⚠ {field_name}选择可能失败: 期望{value_to_select}, 当前{selected_value}")
                    except Exception as e:
                        logger.warning(f"  ✗ 选择{field_name}失败: {e}")
            
            logger.info("✓ 生日填写完成")
            
        except Exception as e:
            logger.warning(f"填写生日失败: {e}")
            # 继续执行，不阻断流程
    
    def _handle_captcha(self) -> bool:
        """处理人机验证"""
        try:
            logger.info("步骤6: 处理人机验证")
            
            # 检查是否有重试按钮
            self._handle_retry_if_exists()
            
            # 快速检查是否直接跳过了验证（出现了验证码输入框）
            logger.info("快速检查页面状态...")
            code_input = self.page.ele('tag:input@autocomplete=one-time-code', timeout=2)
            if code_input:
                logger.info("✓ 未触发人机验证，直接进入验证码页面")
                return True
            
            # 检查是否需要人机验证
            logger.info("检查是否需要人机验证...")
            verify_btn = self.page.ele('text:验证', timeout=3)
            if not verify_btn:
                verify_btn = self.page.ele('text:Verify', timeout=1)
            
            if not verify_btn:
                # 再次确认是否进入了验证码页面（防止刚才加载慢没检测到）
                code_input = self.page.ele('tag:input@autocomplete=one-time-code', timeout=2)
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
                
                # 等待验证完成 - 使用 DrissionPage 的 wait
                # 等待验证按钮消失
                start_time = time.time()
                while time.time() - start_time < 300:
                    verify_btn = self.page.ele('text:验证', timeout=1)
                    if not verify_btn:
                        verify_btn = self.page.ele('text:Verify', timeout=1)
                    
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
            
            # 检查页面是否正常
            try:
                current_url = self.page.url
                logger.info(f"当前页面: {current_url}")
            except Exception as e:
                logger.error(f"无法获取页面URL: {e}")
                logger.error("页面可能已被阻止或断开连接")
                return False
            
            # 等待验证码输入框 - 使用 DrissionPage 的 ele 方法，增加重试
            logger.info("查找验证码输入框...")
            code_input = None
            for attempt in range(5):
                try:
                    code_input = self.page.ele('tag:input@autocomplete=one-time-code', timeout=10)
                    if code_input:
                        logger.info(f"✓ 找到验证码输入框（尝试{attempt+1}）")
                        break
                    
                    # 也尝试其他定位方式
                    code_input = self.page.ele('tag:input@name=verficationCode', timeout=5)
                    if code_input:
                        logger.info(f"✓ 找到验证码输入框（备用方式）")
                        break
                    
                    logger.info(f"  未找到验证码输入框，重试... ({attempt+1}/5)")
                    self._random_wait(2, 3)
                except Exception as e:
                    logger.warning(f"  查找失败: {e}")
                    self._random_wait(2, 3)
            
            if not code_input:
                logger.warning("未找到验证码输入框，可能需要人工介入")
                logger.warning("请在浏览器中查看当前页面状态")
                self._random_wait(5, 10)  # 给时间观察
                return True
            
            # 获取验证码
            code = self.service.request_email_code(self.email)
            logger.info(f"获取到验证码: {code}")
            
            # 输入验证码
            code_input.input(code)
            self._random_wait(1, 2)
            
            # 点击下一步
            next_btn = self.page.ele('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self.page.ele('text:Next', timeout=2)
            
            if next_btn:
                next_btn.click()
                self._random_wait(2, 3)
                
                # 点击后可能出现重试
                self._handle_retry_if_exists()
            
            return True
            
        except Exception as e:
            logger.error(f"输入验证码失败: {e}")
            return False
    
    def _set_password(self) -> bool:
        """设置密码"""
        try:
            logger.info("步骤8: 设置密码")
            
            # 查找密码输入框
            pwd_input = self.page.ele('tag:input@type=password', timeout=30)
            if not pwd_input:
                logger.warning("未找到密码输入框")
                return True
            
            # 输入密码
            pwd_input.input(self.password)
            self._random_wait(1, 2)
            
            # 点击下一步
            next_btn = self.page.ele('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self.page.ele('text:Next', timeout=2)
            
            if next_btn:
                next_btn.click()
                self._random_wait(2, 3)
                
                # 点击后可能出现重试
                self._handle_retry_if_exists()
            
            return True
            
        except Exception as e:
            logger.error(f"设置密码失败: {e}")
            return False
    
    def _skip_profile_photo(self) -> bool:
        """跳过头像上传"""
        try:
            logger.info("步骤9: 跳过头像上传")
            
            skip_btn = self.page.ele('text:Skip for now', timeout=10)
            if not skip_btn:
                skip_btn = self.page.ele('text:跳过', timeout=2)
            
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
            
            username_input = self.page.ele('tag:input@autocomplete=username', timeout=30)
            if not username_input:
                logger.warning("未找到用户名输入框")
                return False
            
            # 尝试多次直到成功
            for attempt in range(10):
                self.username = self._generate_username(self.name)
                logger.info(f"尝试用户名: {self.username}")
                
                username_input.clear()
                username_input.input(self.username)
                self._random_wait(1, 2)
                
                # 检查是否有错误提示
                error = self.page.ele('text:已被使用', timeout=2)
                if not error:
                    error = self.page.ele('text:isn\'t available', timeout=1)
                
                if not error:
                    logger.info(f"✓ 用户名可用: {self.username}")
                    break
                    
                logger.warning(f"用户名已被使用: {self.username}")
            
            # 点击下一步
            next_btn = self.page.ele('text:下一步', timeout=5)
            if not next_btn:
                next_btn = self.page.ele('text:Next', timeout=2)
            if not next_btn:
                next_btn = self.page.ele('text:注册', timeout=2)
            
            if next_btn:
                next_btn.click()
                self._random_wait(2, 3)
                
                # 点击后可能出现重试
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
                
                # 查找跳过按钮 - DrissionPage 多种定位
                skip_btn = self.page.ele('text:Skip', timeout=3)
                if not skip_btn:
                    skip_btn = self.page.ele('text:跳过', timeout=1)
                if not skip_btn:
                    skip_btn = self.page.ele('text:Not now', timeout=1)
                if not skip_btn:
                    skip_btn = self.page.ele('text:Next', timeout=1)
                
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
    
    # 辅助函数
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
        
        # 确定该月的天数
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
        """关闭浏览器 - DrissionPage 自动管理"""
        try:
            if self.page:
                self.page.quit()
                logger.info("浏览器已关闭")
        except:
            pass

