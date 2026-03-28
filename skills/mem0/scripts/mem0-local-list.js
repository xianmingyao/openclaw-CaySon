#!/usr/bin/env node
/**
 * 本地列出所有记忆脚本（使用Ollama + ChromaDB）
 */
import { getMem0Instance, USER_ID } from "./mem0-local-config.js";

async function main() {
    try {
        const memory = getMem0Instance();
        
        console.log("📋 获取所有记忆...\n");
        
        const results = await memory.getAll({
            user_id: USER_ID
        });
        
        if (results && results.length > 0) {
            console.log(`找到 ${results.length} 条记忆:\n`);
            results.forEach((item, i) => {
                console.log(`--- 记忆 ${i + 1} ---`);
                console.log(`ID: ${item.id}`);
                console.log(`内容: ${item.memory || item.text || JSON.stringify(item)}`);
                if (item.created_at) {
                    console.log(`创建时间: ${new Date(item.created_at).toLocaleString()}`);
                }
                console.log();
            });
        } else {
            console.log("没有存储任何记忆");
        }
        
    } catch (error) {
        console.error("获取失败:", error.message);
        if (error.message.includes("connect")) {
            console.log("\n⚠️ 确保Ollama正在运行: ollama serve");
        }
    }
}

main();
