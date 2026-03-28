#!/usr/bin/env node
/**
 * Mem0 本地配置（使用 Ollama）
 * 不需要OpenAI API Key，完全本地运行
 */

import { Memory } from "mem0ai/oss";
import * as path from "path";
import * as os from "os";
import * as fs from "fs";

const MEM0_DIR = path.join(os.homedir(), ".mem0");
const HISTORY_DB = path.join(MEM0_DIR, "history.db");

// 确保目录存在
if (!fs.existsSync(MEM0_DIR)) {
    fs.mkdirSync(MEM0_DIR, { recursive: true });
}

/**
 * 获取Mem0实例（本地Ollama配置）
 * @returns {Memory} 配置好的Memory实例
 */
export function getMem0Instance(options = {}) {
    const config = {
        version: "v1.1",
        
        // Ollama 本地Embedding
        embedder: {
            provider: "ollama",
            config: {
                model: "nomic-embed-text",
                url: "http://localhost:11434"
            }
        },
        
        // 本地向量存储（使用内存，持久化到文件）
        vectorStore: {
            provider: "memory",
            config: {
                collectionName: "clawdbot_memories"
            }
        },
        
        // 不使用自动LLM提取，手动添加
        // llm: { provider: "ollama", config: { model: "llama3.2", url: "http://localhost:11434" } },
        
        historyDbPath: HISTORY_DB,
        ...options
    };

    return new Memory(config);
}

/**
 * 用户ID
 */
export const USER_ID = "ningcaison";
