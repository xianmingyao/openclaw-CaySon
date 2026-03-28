/**
 * 使用human-browser登录有道云笔记并写入内容
 */
const { launchHuman, sleep } = require('C:/Users/Administrator/.agents/skills/human-browser/scripts/browser-human');

async function main() {
    console.log('启动human-browser...');
    const { page } = await launchHuman({ mobile: false });
    
    // 打开有道云笔记
    console.log('打开有道云笔记...');
    await page.goto('https://note.youdao.com/web/', { timeout: 60000 });
    await sleep(5000);
    
    // 截图
    await page.screenshot({ path: 'youdao1.png' });
    console.log('截图1: youdao1.png');
    
    // 查找并点击微信登录
    console.log('尝试登录...');
    
    // 查找所有图片按钮
    const imgs = await page.$$('img');
    console.log(`找到 ${imgs.length} 个图片`);
    
    // 尝试点击登录区域的图片
    const loginArea = await page.$('.login-tab-content');
    if (loginArea) {
        console.log('找到登录区域');
    }
    
    // 尝试直接输入手机号登录
    const phoneInput = await page.$('input[placeholder*="手机号"]');
    if (phoneInput) {
        console.log('找到手机号输入框，输入...');
        await phoneInput.click();
        await page.keyboard.type('你的手机号'); // 需要填写
    }
    
    // 截图看状态
    await page.screenshot({ path: 'youdao2.png' });
    console.log('截图2: youdao2.png');
    
    console.log('完成!');
    await sleep(3000);
}

main().catch(e => {
    console.error('错误:', e.message);
    process.exit(1);
});
