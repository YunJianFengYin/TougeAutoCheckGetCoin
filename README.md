# Educoder自动签到工具

## 功能说明
此工具用于自动登录Educoder网站并执行签到领取金币操作。

## 安装依赖
```bash
pip install selenium requests webdriver-manager
```

## 使用方法
1. 运行脚本后按提示输入用户名和密码
2. 或者创建`educoder_config.json`文件保存凭证
  例如
```educoder_config.json
{
  "username": "在此处填入你的账号",
  "password": "在此处填入你的密码"
}
```
4. 脚本会自动打开浏览器执行签到操作

## 注意事项
1. 请确保遵守Educoder网站的服务条款
2. 频繁的自动化操作可能导致账户被限制
3. 仅用于学习目的，不得滥用

## 免责声明
使用此工具造成的任何后果由使用者自行承担。
