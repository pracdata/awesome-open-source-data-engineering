package com.agentwarehouses.mcp;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Smoke test verifying the MCP SDK is available on the classpath.
 */
class McpSdkAvailableTest {

    @Test
    void mcpSdkClassesAvailable() throws ClassNotFoundException {
        Class<?> mcpSchema = Class.forName("io.modelcontextprotocol.spec.McpSchema");
        assertNotNull(mcpSchema, "McpSchema class should be on the classpath");
    }
}
