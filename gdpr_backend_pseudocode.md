# GDPR Backend Implementation - Pseudo-code

## 1. Database Schema Extensions

```pseudo
// Add GDPR-related fields to user table
TABLE users:
    id: UUID PRIMARY KEY
    email: STRING UNIQUE NOT NULL
    password_hash: STRING NOT NULL  // bcrypt hashed
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
    deleted_at: TIMESTAMP NULL  // Soft delete marker
    deletion_requested_at: TIMESTAMP NULL
    data_processing_consent: BOOLEAN DEFAULT false
    marketing_consent: BOOLEAN DEFAULT false
    last_login: TIMESTAMP

// Audit log for GDPR compliance
TABLE gdpr_audit_log:
    id: UUID PRIMARY KEY
    user_id: UUID FOREIGN KEY REFERENCES users(id)
    action_type: ENUM('export', 'delete', 'access', 'rectify')
    timestamp: TIMESTAMP
    ip_address: STRING
    user_agent: STRING
    details: JSONB

// Data processing agreements tracking
TABLE data_processors:
    id: UUID PRIMARY KEY
    name: STRING  // e.g., "Anthropic", "Fly.io"
    dpa_url: STRING
    dpa_version: STRING
    last_reviewed: DATE
    is_active: BOOLEAN
```

## 2. User Rights - Data Export

```pseudo
// Endpoint: GET /api/user/export
FUNCTION exportUserData(userId: UUID) -> JSON:
    // Authenticate user
    IF NOT authenticated(userId):
        RETURN error(401, "Unauthorized")

    // Log the export action
    logGDPRAction(userId, 'export', getCurrentIP(), getUserAgent())

    // Collect all user data
    userData = {
        account: getUserAccount(userId),
        tasks: getUserTasks(userId),
        chat_history: getAIChatHistory(userId),
        time_tracking: getTimeTracking(userId),
        labels: getUserLabels(userId),
        preferences: getUserPreferences(userId),
        export_metadata: {
            exported_at: getCurrentTimestamp(),
            format_version: "1.0",
            gdpr_compliant: true
        }
    }

    RETURN JSON(userData)

// Helper function to get user account data
FUNCTION getUserAccount(userId: UUID) -> Object:
    user = SELECT email, created_at, updated_at, last_login
            FROM users
            WHERE id = userId

    RETURN {
        email: user.email,
        account_created: user.created_at,
        last_updated: user.updated_at,
        last_login: user.last_login
    }

// Helper function to get all user tasks
FUNCTION getUserTasks(userId: UUID) -> Array:
    tasks = SELECT * FROM tasks
            WHERE user_id = userId
            ORDER BY created_at DESC

    RETURN tasks.map(task => {
        id: task.id,
        title: task.title,
        description: task.description,
        status: task.status,
        labels: task.labels,
        created_at: task.created_at,
        updated_at: task.updated_at,
        completed_at: task.completed_at
    })

// Helper function to get AI chat history
FUNCTION getAIChatHistory(userId: UUID) -> Array:
    chats = SELECT * FROM ai_chat_history
            WHERE user_id = userId
            ORDER BY created_at DESC

    RETURN chats.map(chat => {
        id: chat.id,
        user_message: chat.user_message,
        ai_response: chat.ai_response,
        timestamp: chat.created_at,
        task_context: chat.task_id
    })

// Helper function to get time tracking data
FUNCTION getTimeTracking(userId: UUID) -> Array:
    timeEntries = SELECT * FROM time_entries
                  WHERE user_id = userId
                  ORDER BY start_time DESC

    RETURN timeEntries.map(entry => {
        task_id: entry.task_id,
        start_time: entry.start_time,
        end_time: entry.end_time,
        duration_seconds: entry.duration,
        notes: entry.notes
    })
```

## 3. User Rights - Account Deletion

```pseudo
// Endpoint: DELETE /api/user/account
FUNCTION deleteUserAccount(userId: UUID, confirmation: Boolean) -> Response:
    // Authenticate user
    IF NOT authenticated(userId):
        RETURN error(401, "Unauthorized")

    // Require explicit confirmation
    IF NOT confirmation:
        RETURN error(400, "Deletion confirmation required")

    // Log the deletion request
    logGDPRAction(userId, 'delete', getCurrentIP(), getUserAgent())

    // Soft delete - mark for deletion
    BEGIN TRANSACTION:
        UPDATE users
        SET deleted_at = NOW(),
            deletion_requested_at = NOW()
        WHERE id = userId

        // Optional: Keep for 30 days recovery period
        // The hard delete will be done by a cron job
    COMMIT TRANSACTION

    // Invalidate all JWT tokens for this user
    revokeAllUserTokens(userId)

    RETURN success({
        message: "Account marked for deletion. All data will be permanently removed in 30 days.",
        recovery_deadline: addDays(NOW(), 30)
    })

// Endpoint: POST /api/user/recover (within 30 days)
FUNCTION recoverDeletedAccount(userId: UUID) -> Response:
    user = SELECT * FROM users WHERE id = userId

    IF user.deleted_at IS NULL:
        RETURN error(400, "Account is not marked for deletion")

    IF user.deletion_requested_at < subtractDays(NOW(), 30):
        RETURN error(410, "Recovery period has expired")

    // Restore account
    UPDATE users
    SET deleted_at = NULL,
        deletion_requested_at = NULL
    WHERE id = userId

    logGDPRAction(userId, 'recover', getCurrentIP(), getUserAgent())

    RETURN success({ message: "Account recovered successfully" })

// Cron job: Run daily to hard delete expired accounts
FUNCTION cleanupDeletedAccounts() -> Void:
    // Find accounts deleted more than 30 days ago
    expiredAccounts = SELECT id FROM users
                      WHERE deleted_at IS NOT NULL
                      AND deleted_at < subtractDays(NOW(), 30)

    FOR EACH accountId IN expiredAccounts:
        BEGIN TRANSACTION:
            // Delete cascades to all related tables due to foreign keys
            DELETE FROM ai_chat_history WHERE user_id = accountId
            DELETE FROM time_entries WHERE user_id = accountId
            DELETE FROM tasks WHERE user_id = accountId
            DELETE FROM user_preferences WHERE user_id = accountId
            DELETE FROM gdpr_audit_log WHERE user_id = accountId
            DELETE FROM users WHERE id = accountId

            logSystemAction('hard_delete', accountId, "Account permanently deleted after 30 days")
        COMMIT TRANSACTION
```

## 4. Data Security - Access Controls

```pseudo
// Middleware: Ensure users can only access their own data
FUNCTION enforceUserDataAccess(req: Request, res: Response, next: Function):
    userId = req.user.id  // From JWT token

    // For any request with userId parameter, verify it matches authenticated user
    IF req.params.userId AND req.params.userId != userId:
        RETURN error(403, "Forbidden: Cannot access other users' data")

    // Attach userId to request for query validation
    req.authenticatedUserId = userId
    next()

// Example: Secure task retrieval
FUNCTION getTask(taskId: UUID, authenticatedUserId: UUID) -> Task:
    task = SELECT * FROM tasks
           WHERE id = taskId
           AND user_id = authenticatedUserId  // Critical: Ensure ownership

    IF task IS NULL:
        THROW error(404, "Task not found or access denied")

    RETURN task

// Example: Secure task update
FUNCTION updateTask(taskId: UUID, userId: UUID, updates: Object) -> Task:
    // First verify ownership
    task = SELECT * FROM tasks
           WHERE id = taskId
           AND user_id = userId

    IF task IS NULL:
        THROW error(404, "Task not found or access denied")

    // Proceed with update
    UPDATE tasks
    SET title = COALESCE(updates.title, title),
        description = COALESCE(updates.description, description),
        status = COALESCE(updates.status, status),
        updated_at = NOW()
    WHERE id = taskId
    AND user_id = userId  // Double-check ownership

    RETURN getTask(taskId, userId)

// Example: Secure AI chat history
FUNCTION getAIChat(chatId: UUID, userId: UUID) -> Chat:
    chat = SELECT * FROM ai_chat_history
           WHERE id = chatId
           AND user_id = userId  // Ensure ownership

    IF chat IS NULL:
        THROW error(404, "Chat not found or access denied")

    RETURN chat
```

## 5. AI Integration - Data Minimization

```pseudo
// When sending data to Anthropic API
FUNCTION generateAISuggestion(taskId: UUID, userId: UUID) -> String:
    // Get task with ownership verification
    task = getTask(taskId, userId)

    // Data minimization: Only send what's necessary
    aiPayload = {
        task_title: task.title,
        task_description: task.description,
        task_labels: task.labels
        // DO NOT send: user email, user_id, passwords, etc.
    }

    // Call Anthropic API
    response = callAnthropicAPI(aiPayload)

    // Store AI interaction for user's records
    INSERT INTO ai_chat_history (
        user_id,
        task_id,
        user_message,
        ai_response,
        created_at
    ) VALUES (
        userId,
        taskId,
        aiPayload.task_description,
        response.content,
        NOW()
    )

    RETURN response.content

// Sanitize data before sending to external APIs
FUNCTION sanitizeForExternalAPI(data: Object) -> Object:
    // Remove all personally identifiable information
    sanitized = {}

    ALLOWED_FIELDS = ['title', 'description', 'labels', 'status']

    FOR EACH field IN data:
        IF field IN ALLOWED_FIELDS:
            sanitized[field] = data[field]

    RETURN sanitized
```

## 6. Consent Management

```pseudo
// Endpoint: POST /api/user/consent
FUNCTION updateConsent(userId: UUID, consentType: String, granted: Boolean) -> Response:
    IF NOT authenticated(userId):
        RETURN error(401, "Unauthorized")

    validTypes = ['data_processing', 'marketing', 'analytics']

    IF consentType NOT IN validTypes:
        RETURN error(400, "Invalid consent type")

    // Update consent
    UPDATE users
    SET {consentType}_consent = granted,
        updated_at = NOW()
    WHERE id = userId

    // Log consent change
    logGDPRAction(userId, 'consent_update', getCurrentIP(), getUserAgent(), {
        consent_type: consentType,
        granted: granted
    })

    RETURN success({ message: "Consent updated successfully" })

// Get user consent status
FUNCTION getUserConsent(userId: UUID) -> Object:
    user = SELECT data_processing_consent,
                  marketing_consent,
                  analytics_consent
           FROM users
           WHERE id = userId

    RETURN {
        data_processing: user.data_processing_consent,
        marketing: user.marketing_consent,
        analytics: user.analytics_consent
    }
```

## 7. Data Retention Policies

```pseudo
// Configuration
CONST RETENTION_POLICIES = {
    deleted_accounts: 30,  // days
    ai_chat_logs: 365,     // days (or until account deletion)
    audit_logs: 730,       // 2 years for compliance
    anonymous_analytics: -1  // forever (if truly anonymized)
}

// Cron job: Clean up old AI chat history
FUNCTION cleanupOldAIChatHistory() -> Void:
    cutoffDate = subtractDays(NOW(), RETENTION_POLICIES.ai_chat_logs)

    DELETE FROM ai_chat_history
    WHERE created_at < cutoffDate
    AND user_id IN (SELECT id FROM users WHERE deleted_at IS NOT NULL)

    logSystemAction('cleanup', 'ai_chat_history', "Removed chat logs older than retention policy")

// Cron job: Clean up old audit logs
FUNCTION cleanupOldAuditLogs() -> Void:
    cutoffDate = subtractDays(NOW(), RETENTION_POLICIES.audit_logs)

    DELETE FROM gdpr_audit_log
    WHERE timestamp < cutoffDate

    logSystemAction('cleanup', 'gdpr_audit_log', "Removed audit logs older than retention policy")
```

## 8. GDPR Audit Logging

```pseudo
// Log all GDPR-related actions
FUNCTION logGDPRAction(
    userId: UUID,
    actionType: String,
    ipAddress: String,
    userAgent: String,
    details: Object = {}
) -> Void:
    INSERT INTO gdpr_audit_log (
        id,
        user_id,
        action_type,
        timestamp,
        ip_address,
        user_agent,
        details
    ) VALUES (
        generateUUID(),
        userId,
        actionType,
        NOW(),
        ipAddress,
        userAgent,
        toJSON(details)
    )

// Get user's GDPR action history
FUNCTION getUserGDPRHistory(userId: UUID) -> Array:
    IF NOT authenticated(userId):
        THROW error(401, "Unauthorized")

    logs = SELECT * FROM gdpr_audit_log
           WHERE user_id = userId
           ORDER BY timestamp DESC
           LIMIT 100

    RETURN logs.map(log => {
        action: log.action_type,
        timestamp: log.timestamp,
        details: log.details
    })
```

## 9. Privacy Policy Acceptance

```pseudo
// Track privacy policy acceptance
TABLE privacy_policy_acceptances:
    id: UUID PRIMARY KEY
    user_id: UUID FOREIGN KEY REFERENCES users(id)
    policy_version: STRING
    accepted_at: TIMESTAMP
    ip_address: STRING
    user_agent: STRING

// Endpoint: POST /api/user/accept-privacy-policy
FUNCTION acceptPrivacyPolicy(userId: UUID, policyVersion: String) -> Response:
    IF NOT authenticated(userId):
        RETURN error(401, "Unauthorized")

    INSERT INTO privacy_policy_acceptances (
        id,
        user_id,
        policy_version,
        accepted_at,
        ip_address,
        user_agent
    ) VALUES (
        generateUUID(),
        userId,
        policyVersion,
        NOW(),
        getCurrentIP(),
        getUserAgent()
    )

    RETURN success({ message: "Privacy policy accepted" })

// Check if user has accepted current policy
FUNCTION hasAcceptedCurrentPolicy(userId: UUID) -> Boolean:
    CURRENT_POLICY_VERSION = "1.0"

    acceptance = SELECT * FROM privacy_policy_acceptances
                 WHERE user_id = userId
                 AND policy_version = CURRENT_POLICY_VERSION
                 ORDER BY accepted_at DESC
                 LIMIT 1

    RETURN acceptance IS NOT NULL
```

## 10. Data Breach Notification System

```pseudo
// In case of data breach - GDPR requires notification within 72 hours
TABLE data_breach_incidents:
    id: UUID PRIMARY KEY
    discovered_at: TIMESTAMP
    breach_type: STRING
    affected_users_count: INTEGER
    severity: ENUM('low', 'medium', 'high', 'critical')
    description: TEXT
    mitigation_steps: TEXT
    authorities_notified_at: TIMESTAMP NULL
    users_notified_at: TIMESTAMP NULL
    resolved_at: TIMESTAMP NULL

// Record a data breach
FUNCTION recordDataBreach(
    breachType: String,
    affectedUserIds: Array<UUID>,
    severity: String,
    description: String
) -> UUID:
    breachId = generateUUID()

    INSERT INTO data_breach_incidents (
        id,
        discovered_at,
        breach_type,
        affected_users_count,
        severity,
        description
    ) VALUES (
        breachId,
        NOW(),
        breachType,
        affectedUserIds.length,
        severity,
        description
    )

    // Alert administrators
    alertAdmins(breachId, severity)

    // If high/critical, prepare for 72-hour notification
    IF severity IN ['high', 'critical']:
        scheduleBreachNotification(breachId, affectedUserIds)

    RETURN breachId

// Notify affected users
FUNCTION notifyAffectedUsers(breachId: UUID, userIds: Array<UUID>) -> Void:
    breach = SELECT * FROM data_breach_incidents WHERE id = breachId

    FOR EACH userId IN userIds:
        user = SELECT email FROM users WHERE id = userId

        sendEmail(user.email, {
            subject: "Important Security Notice",
            body: composeBreachNotificationEmail(breach)
        })

        logGDPRAction(userId, 'breach_notification', 'SYSTEM', 'SYSTEM', {
            breach_id: breachId,
            severity: breach.severity
        })

    UPDATE data_breach_incidents
    SET users_notified_at = NOW()
    WHERE id = breachId
```

## 11. Rate Limiting for GDPR Endpoints

```pseudo
// Prevent abuse of data export/deletion
TABLE gdpr_rate_limits:
    user_id: UUID PRIMARY KEY
    last_export_at: TIMESTAMP NULL
    export_count_today: INTEGER DEFAULT 0
    last_deletion_attempt_at: TIMESTAMP NULL

// Rate limit configuration
CONST RATE_LIMITS = {
    exports_per_day: 5,
    deletion_cooldown_hours: 24
}

// Check if user can export data
FUNCTION canExportData(userId: UUID) -> Boolean:
    limits = SELECT * FROM gdpr_rate_limits WHERE user_id = userId

    IF limits IS NULL:
        // First time, allow
        INSERT INTO gdpr_rate_limits (user_id, export_count_today, last_export_at)
        VALUES (userId, 0, NULL)
        RETURN true

    // Reset daily count if new day
    IF limits.last_export_at < startOfDay(NOW()):
        UPDATE gdpr_rate_limits
        SET export_count_today = 0
        WHERE user_id = userId
        RETURN true

    // Check daily limit
    IF limits.export_count_today >= RATE_LIMITS.exports_per_day:
        RETURN false

    RETURN true

// Track export usage
FUNCTION trackExportUsage(userId: UUID) -> Void:
    UPDATE gdpr_rate_limits
    SET export_count_today = export_count_today + 1,
        last_export_at = NOW()
    WHERE user_id = userId
```

## 12. Encryption Helpers

```pseudo
// Encrypt sensitive data at rest (optional, for extra security)
FUNCTION encryptSensitiveData(data: String, key: String) -> String:
    // Use AES-256-GCM encryption
    encrypted = aesEncrypt(data, key, algorithm='AES-256-GCM')
    RETURN base64Encode(encrypted)

FUNCTION decryptSensitiveData(encryptedData: String, key: String) -> String:
    decoded = base64Decode(encryptedData)
    decrypted = aesDecrypt(decoded, key, algorithm='AES-256-GCM')
    RETURN decrypted

// Example: Encrypt AI chat history
FUNCTION storeEncryptedChatHistory(
    userId: UUID,
    taskId: UUID,
    userMessage: String,
    aiResponse: String
) -> UUID:
    encryptionKey = getEncryptionKey(userId)  // User-specific or app-wide key

    encryptedUserMessage = encryptSensitiveData(userMessage, encryptionKey)
    encryptedAIResponse = encryptSensitiveData(aiResponse, encryptionKey)

    chatId = INSERT INTO ai_chat_history (
        id,
        user_id,
        task_id,
        user_message,  // Encrypted
        ai_response,   // Encrypted
        created_at
    ) VALUES (
        generateUUID(),
        userId,
        taskId,
        encryptedUserMessage,
        encryptedAIResponse,
        NOW()
    ) RETURNING id

    RETURN chatId

// Retrieve and decrypt
FUNCTION getDecryptedChatHistory(userId: UUID) -> Array:
    encryptionKey = getEncryptionKey(userId)

    chats = SELECT * FROM ai_chat_history WHERE user_id = userId

    RETURN chats.map(chat => {
        id: chat.id,
        user_message: decryptSensitiveData(chat.user_message, encryptionKey),
        ai_response: decryptSensitiveData(chat.ai_response, encryptionKey),
        created_at: chat.created_at
    })
```

## 13. Sub-processor Management

```pseudo
// Track which processors handle user data
FUNCTION getActiveDataProcessors() -> Array:
    processors = SELECT * FROM data_processors WHERE is_active = true

    RETURN processors.map(p => {
        name: p.name,
        dpa_url: p.dpa_url,
        last_reviewed: p.last_reviewed
    })

// Update processor DPA
FUNCTION updateProcessorDPA(processorId: UUID, dpaUrl: String, version: String) -> Void:
    UPDATE data_processors
    SET dpa_url = dpaUrl,
        dpa_version = version,
        last_reviewed = NOW()
    WHERE id = processorId

    logSystemAction('dpa_update', processorId, "Updated DPA for processor")

// Example: Seed initial processors
FUNCTION seedDataProcessors() -> Void:
    processors = [
        {
            name: "Anthropic",
            dpa_url: "https://www.anthropic.com/legal/commercial-terms",
            dpa_version: "2024-01",
            is_active: true
        },
        {
            name: "Fly.io",
            dpa_url: "https://fly.io/legal/terms",
            dpa_version: "2024-01",
            is_active: true
        },
        {
            name: "Vercel",
            dpa_url: "https://vercel.com/legal/dpa",
            dpa_version: "2024-01",
            is_active: true
        }
    ]

    FOR EACH processor IN processors:
        INSERT INTO data_processors (id, name, dpa_url, dpa_version, last_reviewed, is_active)
        VALUES (
            generateUUID(),
            processor.name,
            processor.dpa_url,
            processor.dpa_version,
            NOW(),
            processor.is_active
        )
```

## 14. Main Application Entry Points

```pseudo
// Express.js-style API routes
ROUTES:
    // User Rights
    GET    /api/user/export                 -> exportUserData(req.user.id)
    DELETE /api/user/account                -> deleteUserAccount(req.user.id, req.body.confirmation)
    POST   /api/user/recover                -> recoverDeletedAccount(req.user.id)
    GET    /api/user/gdpr-history           -> getUserGDPRHistory(req.user.id)

    // Consent Management
    GET    /api/user/consent                -> getUserConsent(req.user.id)
    POST   /api/user/consent                -> updateConsent(req.user.id, req.body.type, req.body.granted)

    // Privacy Policy
    POST   /api/user/accept-privacy-policy  -> acceptPrivacyPolicy(req.user.id, req.body.version)

    // Data Processors (public endpoint)
    GET    /api/gdpr/processors             -> getActiveDataProcessors()

// Cron Jobs
SCHEDULED_JOBS:
    DAILY at 02:00  -> cleanupDeletedAccounts()
    DAILY at 03:00  -> cleanupOldAIChatHistory()
    WEEKLY          -> cleanupOldAuditLogs()
```

## 15. Error Handling

```pseudo
// Custom GDPR-related errors
CLASS GDPRError EXTENDS Error:
    CONSTRUCTOR(message: String, code: String):
        this.message = message
        this.code = code
        this.statusCode = 400

CLASS RateLimitError EXTENDS GDPRError:
    CONSTRUCTOR(message: String):
        SUPER(message, 'RATE_LIMIT_EXCEEDED')
        this.statusCode = 429

CLASS DataAccessError EXTENDS GDPRError:
    CONSTRUCTOR(message: String):
        SUPER(message, 'DATA_ACCESS_DENIED')
        this.statusCode = 403

// Global error handler
FUNCTION handleGDPRError(error: Error, req: Request, res: Response):
    IF error INSTANCEOF GDPRError:
        RETURN res.status(error.statusCode).json({
            error: error.code,
            message: error.message
        })

    // Log unexpected errors
    logSystemError(error, req)

    RETURN res.status(500).json({
        error: 'INTERNAL_ERROR',
        message: 'An unexpected error occurred'
    })
```

---

## Implementation Priority

### Phase 1 - MVP (1-2 days):
1. ✅ Data export endpoint
2. ✅ Account deletion endpoint
3. ✅ Access control middleware
4. ✅ GDPR audit logging

### Phase 2 - Launch-ready (3-5 days):
1. ✅ Consent management
2. ✅ Privacy policy acceptance tracking
3. ✅ Rate limiting
4. ✅ Cron jobs for cleanup

### Phase 3 - Enterprise (1-2 weeks):
1. ✅ Encryption at rest
2. ✅ Data breach notification system
3. ✅ Advanced audit logs
4. ✅ Sub-processor management dashboard

---

## Testing Checklist

```pseudo
GDPR_TESTS:
    ✓ User can export all their data
    ✓ Exported data includes all tables
    ✓ User can delete their account
    ✓ Deleted accounts are soft-deleted for 30 days
    ✓ Hard delete removes ALL user data
    ✓ Users cannot access other users' data
    ✓ All GDPR actions are logged
    ✓ Rate limiting prevents abuse
    ✓ Consent changes are tracked
    ✓ Privacy policy acceptance is recorded
    ✓ Cron jobs run successfully
    ✓ Data breach notification works
```
