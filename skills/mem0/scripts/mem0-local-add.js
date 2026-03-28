#!/usr/bin/env node
/**
 * 本地添加记忆脚本（使用Ollama + ChromaDB）
 */
import { getMem0Instance, USER_ID } from "./mem0-local-config.js";

const text = process.argv[2];

if (!text) {
    console.error("用法: node mem0-local-add.js <记忆内容>");
    console.error("示例: node mem0-local-add.js \"用户宁采臣是CTO\"");
    process.exit(1);
}

async function main() {
    try {
        const memory = getMem0Instance();
        
        console.log(`➕ 添加记忆: "${text}"`);
        
        const result = await memory.add({
            text: text,
            user_id: USER_ID
        });
        
        if (result && result.id) {
            console.log(`\n✅ 记忆添加成功!`);
            console.log(`📝 ID: ${result.id}`);
        } else {
            console.log("\n✅ 记忆已添加");
        }
        
    } catch (error) {
        console.error("添加失败:", error.message);
        if (error.message.includes("connect")) {
            console.log("\n⚠️ 确保Ollama正在运行: ollama serve");
        }
    }
}

main();
