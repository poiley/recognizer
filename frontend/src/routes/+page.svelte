<script>
    import { onDestroy } from "svelte";
    import * as pdfjsLib from "pdfjs-dist";
    import Spinner from "$lib/components/Spinner.svelte";

    const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000;

    let ws;
    let dropZone;
    let loading = false;
    let summary = "";
    let progress = 0;
    let error = null;
    let warnings = [];
    let retryCount = 0;
    let currentPage = 0;
    let totalPages = 0;
    let status = "";
    let heartbeatTimeout;

    async function connectWebSocket() {
        try {
            ws = new WebSocket("ws://localhost:8000/ws");
            await new Promise((resolve, reject) => {
                ws.onopen = resolve;
                ws.onerror = reject;
            });
            bindWebSocketEvents();
        } catch (e) {
            await handleRetry(e);
        }
    }

    function bindWebSocketEvents() {
        let lastHeartbeat = Date.now();
        const HEARTBEAT_INTERVAL = 10000; // 10 seconds
        const MAX_MISSED_HEARTBEATS = 3;

        function resetHeartbeat() {
            if (heartbeatTimeout) clearTimeout(heartbeatTimeout);
            lastHeartbeat = Date.now();
            heartbeatTimeout = setTimeout(checkHeartbeat, HEARTBEAT_INTERVAL);
        }

        function checkHeartbeat() {
            const timeSinceLastHeartbeat = Date.now() - lastHeartbeat;
            if (
                timeSinceLastHeartbeat >
                HEARTBEAT_INTERVAL * MAX_MISSED_HEARTBEATS
            ) {
                console.error(
                    "[WS] Connection dead - too many missed heartbeats",
                );
                ws.close();
            } else {
                heartbeatTimeout = setTimeout(
                    checkHeartbeat,
                    HEARTBEAT_INTERVAL,
                );
            }
        }

        ws.onmessage = (event) => {
            console.log("[WS] Raw message:", event.data);
            try {
                const data = JSON.parse(event.data);
                if (data.status === "processing" || data.type === "ping") {
                    resetHeartbeat();
                    return;
                }
                console.log("[WS] Parsed:", data);

                if (data.error) {
                    console.error("[WS] Error:", data.error);
                    error = data.error;
                    loading = false;
                } else if (data.status) {
                    console.log("[WS] Status:", data.status);
                    status = data.status;
                    switch (data.status) {
                        case "receiving":
                            if (data.progress) {
                                progress = data.progress;
                                console.log("[WS] Upload progress:", progress);
                            }
                            break;
                        case "processing":
                            progress = 1;
                            break;
                        case "analyzing":
                            console.log("[WS] Analysis started");
                            break;
                        case "complete":
                            console.log("[WS] Processing complete");
                            summary = data.summary;
                            loading = false;
                            ws.send(JSON.stringify({ type: "ack" }));
                            break;
                    }
                } else if (data.warning) {
                    console.warn("[WS] Warning:", data.warning);
                    warnings = [...warnings, data.warning];
                }
            } catch (e) {
                console.error("[WS] Parse error:", e);
                error = "Failed to process server response";
                loading = false;
            }
        };

        ws.onerror = (event) => {
            console.error("[WS] Connection error:", event);
            error = "Connection error";
            loading = false;
        };

        ws.onclose = (event) => {
            console.log(
                "[WS] Closed with code:",
                event.code,
                "reason:",
                event.reason,
            );
            if (event.code !== 1000 && !summary) {
                error = `Connection lost (${event.code})${event.reason ? ": " + event.reason : ""}`;
            }
            loading = false;
        };
    }

    async function handleRetry(e) {
        if (retryCount < MAX_RETRIES) {
            retryCount++;
            await new Promise((r) => setTimeout(r, RETRY_DELAY));
            await connectWebSocket();
        } else {
            error = `Connection failed after ${MAX_RETRIES} attempts: ${e.message}`;
            loading = false;
        }
    }

    async function processFile(file) {
        try {
            if (file.size > MAX_FILE_SIZE) {
                throw new Error(
                    `File too large (max ${MAX_FILE_SIZE / 1024 / 1024}MB)`,
                );
            }

            retryCount = 0;
            error = null;
            warnings = [];
            loading = true;
            status = "";

            if (!file?.type?.includes("pdf")) {
                throw new Error("Please upload a PDF file");
            }

            await connectWebSocket();
            const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
            let offset = 0;

            const base64 = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result.split(",")[1]);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });

            while (offset < base64.length) {
                const chunk = base64.slice(offset, offset + CHUNK_SIZE);
                console.log(`Sending chunk ${offset / CHUNK_SIZE + 1}`);

                ws.send(
                    JSON.stringify({
                        type: offset === 0 ? "start" : "chunk",
                        data: chunk,
                        final: offset + CHUNK_SIZE >= base64.length,
                        total: Math.ceil(base64.length / CHUNK_SIZE),
                        current: Math.floor(offset / CHUNK_SIZE) + 1,
                    }),
                );

                offset += CHUNK_SIZE;
                await new Promise((resolve) => setTimeout(resolve, 100));
            }
        } catch (e) {
            console.error("Error:", e);
            error = e.message;
            loading = false;
        }
    }

    function downloadMarkdown() {
        const blob = new Blob([summary], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "summary.md";
        a.click();
        URL.revokeObjectURL(url);
    }

    onDestroy(() => {
        if (heartbeatTimeout) clearTimeout(heartbeatTimeout);
        if (ws) ws.close();
    });

    $: statusMessage =
        {
            receiving: "Uploading document...",
            processing: "Processing PDF...",
            analyzing: "Analyzing content with AI...",
            complete: "Analysis complete!",
        }[status] || "Ready";
</script>

<div class="max-w-4xl mx-auto">
    <div class="text-sm text-gray-400 mb-2">
        {statusMessage}
    </div>

    <div
        bind:this={dropZone}
        role="button"
        tabindex="0"
        aria-label="Drop zone for PDF files"
        class="file-drop-zone p-12 text-center rounded {error
            ? 'border-red-500'
            : ''}"
        on:drop|preventDefault={(e) => processFile(e.dataTransfer.files[0])}
        on:dragover|preventDefault={() =>
            dropZone.classList.add("border-accent")}
        on:dragleave={() => dropZone.classList.remove("border-accent")}
        on:keydown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
                const input = e.target.querySelector('input[type="file"]');
                input?.click();
            }
        }}
    >
        {#if loading}
            <div class="flex flex-col items-center gap-4">
                <Spinner />
                {#if progress < 1}
                    <div>Uploading PDF ({Math.round(progress * 100)}%)</div>
                {:else}
                    <div>{statusMessage}</div>
                {/if}
                <div class="w-64 h-2 bg-secondary rounded-full">
                    <div
                        class="h-full bg-accent rounded-full transition-all"
                        style="width: {progress * 100}%"
                    ></div>
                </div>
            </div>
        {:else}
            <p>
                Drop PDF here or <label class="text-accent cursor-pointer">
                    browse
                    <input
                        type="file"
                        class="hidden"
                        accept=".pdf"
                        on:change={(e) => processFile(e.target.files[0])}
                    />
                </label>
            </p>
        {/if}
    </div>

    {#if error}
        <div class="mt-4 p-4 bg-red-900/50 text-red-200 rounded">
            {error}
        </div>
    {/if}

    {#if warnings.length > 0}
        <div class="mt-4 space-y-2">
            {#each warnings as warning}
                <div class="p-3 bg-yellow-900/50 text-yellow-200 rounded">
                    {warning}
                </div>
            {/each}
        </div>
    {/if}

    {#if summary}
        <div class="markdown-body mt-8 p-4 rounded">
            {summary}
            <button
                on:click={downloadMarkdown}
                class="mt-4 px-4 py-2 bg-accent rounded hover:bg-accent/80"
            >
                Download Markdown
            </button>
        </div>
    {/if}
</div>
