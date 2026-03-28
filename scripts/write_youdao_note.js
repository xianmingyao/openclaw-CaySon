/**
 * 使用human-browser写入有道云笔记
 */
const { launchHuman, humanType, humanClick, humanScroll, sleep } = require('C:/Users/Administrator/.agents/skills/human-browser/scripts/browser-human');
const fs = require('fs');

// 笔记内容
const content = `今日学习总结 2026-03-28

## GitHub热门项目

### 程序员Sunday推荐 - Claude Code生态5个新工具

| 项目 | Stars | 功能 |
|------|-------|------|
| get-shit-done | 39.3k | 元提示+上下文工程+规范驱动开发 |
| learn-claude-code | 36.5k | 从零构建Claude Code-like AI Agent框架 |
| claude-hud | 11.6k | Claude Code状态可视化 |
| claude-code-action | 6.5k | CI/CD集成工具 |

### gstack - YC CEO开源项目
- Stars: 33.2k
- 作者: Garry Tan（Y Combinator CEO）
- 功能: YC创业方法论封装成15个AI Agent

### agent-browser CDP连接功能
- npx agent-browser --cdp 9222 open url
- npx agent-browser --auto-connect state save ./auth.json

## OpenClaw必装Skills（AI干货局推荐）

| 技能 | 安装量 | 状态 |
|------|--------|------|
| agent-browser | 607K+ | 已安装 |
| self-improving agent | 380K+ | 已安装 |
| email management | 310K+ | 待安装 |
| skill-vetter | - | 已安装 |

## 记忆系统配置

### 检索优先级（铁律）
1. 首选：云端Milvus (8.137.122.11:19530)
2. 备选：本地ChromaDB

### 脚本
- mem0_dual_write.py - 双写
- sync_memories_to_milvus.py - 同步
- show_memories.py - 查看`;

async function main() {
    console.log('启动human-browser...');
    
    // 启动浏览器
    const { page } = await launchHuman({ mobile: false });
    
    // 打开有道云笔记
    console.log('打开有道云笔记...');
    await page.goto('https://note.youdao.com/web/');
    await sleep(5000);
    
    // 等待页面加载
    await sleep(5000);
    
    // 截图
    await page.screenshot({ path: 'youdao_note.png' });
    console.log('截图已保存: youdao_note.png');
    
    // 尝试找到编辑器
    console.log('查找编辑器...');
    
    // 尝试多种选择器
    const selectors = [
        '[contenteditable="true"]',
        '.ql-editor',
        '.ProseMirror',
        '[data-lexical-editor]',
        'textarea'
    ];
    
    let editor = null;
    for (const selector of selectors) {
        try {
            editor = await page.$(selector);
            if (editor) {
                console.log(`找到编辑器: ${selector}`);
                break;
            }
        } catch (e) {}
    }
    
    if (!editor) {
        // 尝试在iframe中查找
        console.log('尝试在iframe中查找...');
        const iframes = await page.$$('iframe');
        console.log(`找到 ${iframes.length} 个iframe`);
        
        for (let i = 0; i < iframes.length; i++) {
            try {
                const frame = iframes[i];
                const frameContent = await frame.contentFrame();
                if (frameContent) {
                    const frameEditor = await frameContent.$('[contenteditable="true"]');
                    if (frameEditor) {
                        console.log(`在iframe ${i}中找到编辑器`);
                        editor = frameEditor;
                        break;
                    }
                }
            } catch (e) {
                console.log(`iframe ${i} 访问失败: ${e.message}`);
            }
        }
    }
    
    if (editor) {
        // 点击编辑器
        await editor.click();
        await sleep(500);
        
        // 输入标题
        console.log('输入标题...');
        await page.keyboard.type('今日学习总结 2026-03-28');
        await page.keyboard.press('Enter');
        await sleep(200);
        
        // 输入内容
        console.log('输入内容...');
        await page.keyboard.type(content);
        
        // 截图
        await page.screenshot({ path: 'youdao_note_content.png' });
        console.log('内容截图已保存: youdao_note_content.png');
        
        // 保存
        await page.keyboard.press('Control+s');
        await sleep(1000);
        console.log('笔记已保存');
    } else {
        console.log('未找到编辑器，尝试直接粘贴...');
        
        // 直接粘贴到剪贴板
        await page.goto('https://note.youdao.com/web/');
        await sleep(3000);
        
        // 点击新建按钮
        const newBtn = await page.$('text=新建');
        if (newBtn) {
            await newBtn.click();
            await sleep(2000);
        }
        
        // 粘贴内容
        await page.keyboard.press('Control+v');
        await sleep(1000);
        
        await page.screenshot({ path: 'youdao_note_paste.png' });
        console.log('粘贴截图已保存: youdao_note_paste.png');
    }
    
    console.log('完成!');
    await sleep(2000);
    await page.browser().close();
}

main().catch(e => {
    console.error('错误:', e);
    process.exit(1);
});
