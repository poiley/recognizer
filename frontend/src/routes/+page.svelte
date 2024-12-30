<script>
    import { onDestroy } from "svelte";
    import * as pdfjsLib from "pdfjs-dist";
    import Spinner from "$lib/components/Spinner.svelte";
    import StatusIndicator from "$lib/components/StatusIndicator.svelte";

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
    let currentChunk = 0;
    let totalChunks = 0;
    let estimatedTime = '';

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

    function handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    }

    function handleDrop(event) {
        event.preventDefault();
        handleFileSelect(event);
    }

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
        const HEARTBEAT_INTERVAL = 7000;  // 7 seconds
        const ANALYSIS_HEARTBEAT_INTERVAL = 30000;  // 30 seconds during analysis
        const MAX_MISSED_HEARTBEATS = 3;
        const MAX_ANALYSIS_MISSED_HEARTBEATS = 10;  // Much more tolerant during analysis
        let missedHeartbeats = 0;

        function resetHeartbeat() {
            if (heartbeatTimeout) clearTimeout(heartbeatTimeout);
            lastHeartbeat = Date.now();
            missedHeartbeats = 0;
            heartbeatTimeout = setTimeout(checkHeartbeat, 
                status === 'analyzing' ? ANALYSIS_HEARTBEAT_INTERVAL : HEARTBEAT_INTERVAL
            );
        }

        function checkHeartbeat() {
            const currentInterval = status === 'analyzing' ? 
                ANALYSIS_HEARTBEAT_INTERVAL : HEARTBEAT_INTERVAL;
            const maxMissed = status === 'analyzing' ? 
                MAX_ANALYSIS_MISSED_HEARTBEATS : MAX_MISSED_HEARTBEATS;
            
            const timeSinceLastHeartbeat = Date.now() - lastHeartbeat;
            if (timeSinceLastHeartbeat > currentInterval) {
                missedHeartbeats++;
                console.warn("[WS] Missed heartbeats:", missedHeartbeats);
                
                if (status === 'analyzing') {
                    if (missedHeartbeats >= maxMissed) {
                        console.warn("[WS] Extended processing time during analysis");
                        if (!warnings.includes("AI analysis in progress - this may take several minutes...")) {
                            warnings = [...warnings, "AI analysis in progress - this may take several minutes..."];
                        }
                    }
                } else if (missedHeartbeats >= maxMissed) {
                    console.error("[WS] Connection dead - too many missed heartbeats");
                    error = "Connection lost";
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.close();
                    }
                    return;
                }
            }
            heartbeatTimeout = setTimeout(checkHeartbeat, currentInterval);
        }

        ws.onmessage = (event) => {
            console.log("[WS] Raw message:", event.data);
            try {
                const data = JSON.parse(event.data);
                console.log("[WS] Parsed:", data);

                resetHeartbeat();
                
                if (data.type === "ping") {
                    return;
                }

                // Handle status updates
                if (data.status) {
                    status = data.status;
                    if (data.progress !== undefined) {
                        progress = data.progress;
                        analysisProgress = data.progress;
                    }
                    if (data.page !== undefined) currentPage = data.page;
                    if (data.total !== undefined) totalPages = data.total;
                    if (data.current_chunk !== undefined) currentChunk = data.current_chunk;
                    if (data.total_chunks !== undefined) totalChunks = data.total_chunks;
                    if (data.estimated_time !== undefined) estimatedTime = data.estimated_time;
                    if (data.summary !== undefined) {
                        summary = data.summary;
                        loading = false;
                    }
                }

                if (data.error) {
                    console.error("[WS] Error:", data.error);
                    error = data.error;
                    loading = false;
                } else if (data.warning) {
                    console.warn("[WS] Warning:", data.warning);
                    warnings = [...warnings, data.warning];
                }
            } catch (e) {
                console.error("[WS] Parse error:", e);
                error = "Failed to process server response";
            }
        };

        ws.onerror = (event) => {
            console.error("[WS] WebSocket error:", event);
            error = "Connection error occurred";
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

        // Start heartbeat checking
        resetHeartbeat();
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

    $: statusMessage = {
        receiving: "Uploading document...",
        converting: "Converting PDF...",
        processing: totalPages ? `Processing page ${currentPage}/${totalPages}...` : "Processing PDF...",
        analyzing: totalChunks ? 
            `Analyzing section ${currentChunk}/${totalChunks}... (${estimatedTime})` : 
            "Analyzing content with AI...",
        complete: "Analysis complete!",
    }[status] || "Ready";

    $: progress = status === "analyzing" ? analysisProgress : 
                 status === "processing" ? currentPage / totalPages : 
                 status === "receiving" ? 0 : 1;
</script>

<div class="container mx-auto px-4 py-8">
    <div 
        class="border-2 border-dashed border-accent rounded-lg p-8 text-center"
        on:dragover|preventDefault={(e) => {
            e.dataTransfer.dropEffect = 'copy';
            dropZone.classList.add("border-accent");
        }}
        on:dragleave={() => dropZone.classList.remove("border-accent")}
        on:drop|preventDefault={(e) => {
            dropZone.classList.remove("border-accent");
            processFile(e.dataTransfer.files[0]);
        }}
        bind:this={dropZone}
    >
        <input 
            type="file" 
            accept=".pdf" 
            on:change={(e) => processFile(e.target.files[0])}
            class="hidden" 
            id="fileInput"
        />
        <label 
            for="fileInput"
            class="cursor-pointer text-accent hover:text-accent-dark"
        >
            Click to upload or drag and drop a PDF file
        </label>
    </div>

    {#if error}
        <div class="mt-4 text-red-500">{error}</div>
    {/if}

    {#if warnings.length > 0}
        <div class="mt-4">
            {#each warnings as warning}
                <div class="text-yellow-500">{warning}</div>
            {/each}
        </div>
    {/if}

    {#if status && status !== 'complete' && status !== ''}
        <StatusIndicator 
            {status}
            {progress}
            {currentPage}
            {totalPages}
            {currentChunk}
            {totalChunks}
            {estimatedTime}
            {warnings}
        />
    {/if}

    {#if summary}
        <div class="mt-8 prose prose-sm max-w-none">
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold mb-4">Summary</h2>
                <div class="whitespace-pre-wrap">{summary}</div>
            </div>
        </div>
    {/if}
</div>

<style>
    /* Custom scrollbar for the summary section */
    .summary-container {
        max-height: 70vh;
        overflow-y: auto;
        padding-right: 1rem;
        scrollbar-width: thin;
        scrollbar-color: var(--accent) var(--secondary);
    }
    
    .summary-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .summary-container::-webkit-scrollbar-track {
        background: var(--secondary);
        border-radius: 4px;
    }
    
    .summary-container::-webkit-scrollbar-thumb {
        background-color: var(--accent);
        border-radius: 4px;
        border: 2px solid var(--secondary);
    }
</style>
