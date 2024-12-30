<script>
    export let status = '';
    export let progress = 0;
    export let currentPage = 0;
    export let totalPages = 0;
    export let currentChunk = 0;
    export let totalChunks = 0;
    export let estimatedTime = '';
    export let warnings = [];

    $: isInFinalAnalysis = status === 'analyzing' && 
        (currentChunk === totalChunks || warnings.some(w => w.includes('Extended processing time')));
    $: message = getStatusMessage(status, progress, currentPage, totalPages, currentChunk, totalChunks, estimatedTime, isInFinalAnalysis);
    $: progressPercent = getProgressPercent(status, progress, isInFinalAnalysis);

    function getProgressPercent(status, progress, isInFinalAnalysis) {
        switch (status) {
            case 'receiving':
            case 'processing':
                return progress;
            case 'analyzing':
                return isInFinalAnalysis ? 0.95 : progress;
            case 'complete':
                return 1;
            default:
                return 0;
        }
    }

    function getStatusMessage(status, progress, currentPage, totalPages, currentChunk, totalChunks, estimatedTime, isInFinalAnalysis) {
        switch (status) {
            case 'receiving':
                return `Uploading PDF (${Math.round(progress * 100)}%)`;
            case 'converting':
                return 'Converting PDF to images...';
            case 'converted':
                return `Ready to process ${totalPages} pages`;
            case 'processing':
                if (totalPages) {
                    return `OCR Processing page ${currentPage} of ${totalPages}`;
                }
                return 'Processing...';
            case 'analyzing':
                if (isInFinalAnalysis) {
                    return 'Generating final summary...';
                }
                if (totalChunks) {
                    return `AI Analysis: Processing section ${currentChunk}/${totalChunks} ${estimatedTime ? `(${estimatedTime})` : ''}`;
                }
                return 'Starting AI analysis...';
            case 'complete':
                return 'Analysis complete!';
            default:
                return 'Ready to process PDF';
        }
    }
</script>

<div class="flex flex-col items-center gap-4">
    <div class="text-lg font-semibold text-accent">{message}</div>
    {#if status !== 'complete' && status !== ''}
        <div class="flex flex-col items-center w-full gap-2">
            <div class="w-64 h-2 bg-secondary rounded-full overflow-hidden">
                <div 
                    class="h-full bg-accent transition-all duration-300 ease-out"
                    style="width: {Math.round(progressPercent * 100)}%"
                ></div>
            </div>
            <div class="text-sm text-gray-400">
                {#if status === 'analyzing'}
                    {#if isInFinalAnalysis}
                        This may take several minutes...
                    {:else}
                        Processing document sections...
                    {/if}
                {:else if status === 'processing'}
                    OCR analysis in progress...
                {/if}
            </div>
        </div>
    {/if}
</div>