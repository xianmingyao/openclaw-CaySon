#!/usr/bin/env node
/**
 * 本地向量搜索脚本（使用Ollama + ChromaDB）
 */
import { getMem0Instance, USER_ID } from "./mem0-local-config.js";

const query = process.argv[2];
const limit = parseInt(process.argv.find(arg => arg.startsWith("--limit="))?.split("=")[1] || "5");

if (!query) {
    console.error("用法: node mem0-local-search.js <查询文本> [--limit=5]");
    process.exit(1);
}

async function main() {
    try {
        const memory = getMem0Instance();
        
        console.log(`🔍 搜索: "${query}"`);
        console.log(`📊 限制: ${limit} 条结果\n`);
        
        const results = await memory.search({
            query: query,
            user_id: USER_ID,
            limit: limit
        });
        
        if (results && results.length > 0) {
            console.log("找到相关记忆:\n");
            results.forEach((result, i) => {
                console.log(`--- 记忆 ${i + 1} (相似度: ${(result.score * 100).toFixed(1)}%) ---`);
                console.log(result.memory);
                console.log();
            });
        } else {
            console.log("没有找到相关记忆");
        }
        
    } catch (error) {
        console.error("搜索失败:", error.message);
        if (error.message.includes("connect")) {
            console.log("\n⚠️ 确保Ollama正在运行: ollama serve");
        }
    }
}

main();
