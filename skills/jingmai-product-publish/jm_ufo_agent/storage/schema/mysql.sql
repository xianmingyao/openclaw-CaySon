CREATE TABLE IF NOT EXISTS jm_tasks (
    task_id VARCHAR(128) PRIMARY KEY,
    xlsx_path VARCHAR(512) NULL,
    workflow_docx_path VARCHAR(512) NULL,
    workflow_version VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    current_row INT NULL,
    total_rows INT UNSIGNED NOT NULL DEFAULT 0,
    pending_rows INT UNSIGNED NOT NULL DEFAULT 0,
    completed_rows INT UNSIGNED NOT NULL DEFAULT 0,
    failed_rows INT UNSIGNED NOT NULL DEFAULT 0,
    state_json LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_products (
    product_id VARCHAR(128) PRIMARY KEY,
    task_id VARCHAR(128) NULL,
    row_index INT NOT NULL,
    row_hash CHAR(64) NULL,
    source_xlsx_path VARCHAR(512) NULL,
    sku VARCHAR(64) NULL,
    title VARCHAR(512) NOT NULL,
    jd_price DECIMAL(12,2) NULL,
    purchase_price DECIMAL(12,2) NULL,
    market_price DECIMAL(12,2) NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    raw_json LONGTEXT NOT NULL,
    enriched_json LONGTEXT NOT NULL,
    jd_data_json JSON NULL,
    normalized_data_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_jm_products_row_index (row_index),
    UNIQUE KEY uk_jm_products_task_row (task_id, row_index),
    UNIQUE KEY uk_jm_products_task_hash (task_id, row_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_product_assets (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(128) NOT NULL,
    task_id VARCHAR(128) NULL,
    row_index INT NULL,
    asset_type VARCHAR(32) NOT NULL,
    local_path VARCHAR(512) NULL,
    remote_url VARCHAR(1024) NULL,
    transform_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    transformed_path VARCHAR(512) NULL,
    metadata_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_jm_product_assets_product (product_id),
    KEY idx_jm_product_assets_task_row (task_id, row_index),
    UNIQUE KEY uk_jm_product_assets_identity (product_id, asset_type, remote_url(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_row_execution_states (
    task_id VARCHAR(128) NOT NULL,
    row_index INT NOT NULL,
    status VARCHAR(32) NOT NULL,
    current_field VARCHAR(128) NULL,
    retry_count INT UNSIGNED NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    page_signature VARCHAR(128) NULL,
    completion_score DECIMAL(5,4) NOT NULL DEFAULT 0,
    completion_passed TINYINT(1) NOT NULL DEFAULT 0,
    completion_details_json JSON NULL,
    evaluation_loop_count INT UNSIGNED NOT NULL DEFAULT 0,
    review_score DECIMAL(5,4) NOT NULL DEFAULT 0,
    review_decision VARCHAR(32) NULL,
    review_details_json JSON NULL,
    draft_evidence_json JSON NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, row_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_field_progress (
    task_id VARCHAR(128) NOT NULL,
    row_index INT NOT NULL,
    field_name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    locator VARCHAR(512) NULL,
    expected_value TEXT NULL,
    actual_value TEXT NULL,
    verified_by VARCHAR(32) NULL,
    attempts INT UNSIGNED NOT NULL DEFAULT 0,
    last_error TEXT NULL,
    evidence_json LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, row_index, field_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_step_logs (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(128) NOT NULL,
    row_index INT NULL,
    node_name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    duration_ms INT UNSIGNED NULL,
    error TEXT NULL,
    metadata_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_jm_step_logs_task_row (task_id, row_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_artifacts (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(128) NOT NULL,
    row_index INT NULL,
    artifact_type VARCHAR(64) NOT NULL,
    storage_path VARCHAR(512) NOT NULL,
    metadata_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_jm_artifacts_task_row (task_id, row_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_locator_cache (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    field_key VARCHAR(128) NOT NULL,
    page_signature VARCHAR(128) NOT NULL,
    selector_type VARCHAR(32) NOT NULL,
    selector_value VARCHAR(512) NOT NULL,
    confidence DECIMAL(4,3) NOT NULL DEFAULT 0,
    hit_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_jm_locator_cache_field_page (field_key, page_signature)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_draft_verifications (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(128) NULL,
    task_id VARCHAR(128) NOT NULL,
    row_index INT NOT NULL,
    draft_url VARCHAR(1024) NULL,
    completion_score DECIMAL(5,4) NOT NULL DEFAULT 0,
    verification_result VARCHAR(32) NOT NULL,
    diff_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_jm_draft_verifications_task_row (task_id, row_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_vlm_calls (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(128) NULL,
    row_index INT NULL,
    call_type VARCHAR(64) NOT NULL,
    model VARCHAR(128) NOT NULL,
    prompt_tokens INT UNSIGNED NOT NULL DEFAULT 0,
    completion_tokens INT UNSIGNED NOT NULL DEFAULT 0,
    latency_ms INT UNSIGNED NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL,
    cache_hit TINYINT(1) NOT NULL DEFAULT 0,
    metadata_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_jm_vlm_calls_task_row (task_id, row_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_graph_checkpoints (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    thread_id VARCHAR(128) NOT NULL,
    checkpoint_id VARCHAR(128) NOT NULL,
    parent_checkpoint_id VARCHAR(128) NULL,
    node_name VARCHAR(128) NULL,
    state_json LONGTEXT NOT NULL,
    metadata_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_jm_graph_checkpoints_thread_checkpoint (thread_id, checkpoint_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jm_graph_pending_writes (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    thread_id VARCHAR(128) NOT NULL,
    task_id VARCHAR(128) NULL,
    channel VARCHAR(128) NOT NULL,
    value_json LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_jm_graph_pending_writes_thread (thread_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
