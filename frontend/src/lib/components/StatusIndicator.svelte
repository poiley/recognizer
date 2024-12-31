<script>
    import { onMount, onDestroy } from 'svelte';
    import { browser } from '$app/environment';

    export let status;
    export let progress = 0;
    export let currentPage = 0;
    export let totalPages = 0;
    export let currentChunk = 0;
    export let totalChunks = 0;
    export let estimatedTime = '';
    export let warnings = [];

    let progressContainer;
    let loadingBar;

    $: isInFinalAnalysis = status === 'analyzing' && 
        (currentChunk === totalChunks || warnings.some(w => w.includes('Extended processing time')));
    $: message = getStatusMessage(status, progress, currentPage, totalPages, currentChunk, totalChunks, estimatedTime, isInFinalAnalysis);
    $: progressPercent = getProgressPercent(status, progress, isInFinalAnalysis);

    onMount(() => {
        if (browser && window.ldBar) {
            const ldBar = document.createElement('div');
            ldBar.className = 'ldBar';
            ldBar.setAttribute('data-preset', 'line');
            ldBar.setAttribute('data-stroke', 'data:ldbar/res,gradient(0,1,#EDE342,#F2BF6C,#F69A97,#FB76C1)');
            ldBar.setAttribute('data-stroke-width', '8');
            ldBar.setAttribute('data-value', '0');
            ldBar.setAttribute('data-label', 'false');
            
            progressContainer.innerHTML = '';
            progressContainer.appendChild(ldBar);
            
            loadingBar = new window.ldBar(ldBar);
            loadingBar.label = false;

            const svg = ldBar.querySelector('svg');
            if (svg) {
                svg.style.width = '100%';
                svg.setAttribute('preserveAspectRatio', 'none');
            }
        }
    });

    $: if (loadingBar && browser) {
        loadingBar.set(progressPercent * 100);
    }

    onDestroy(() => {
        if (loadingBar && progressContainer) {
            progressContainer.innerHTML = '';
        }
    });

    function getProgressPercent(status, progress, isInFinalAnalysis) {
        if (status === 'receiving' || status === 'processing') {
            return progress;
        } else if (status === 'analyzing') {
            return isInFinalAnalysis ? 0.95 : progress;
        } else if (status === 'complete') {
            return 1;
        }
        return 0;
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
                return `OCR processing page ${currentPage} of ${totalPages}`;
            case 'analyzing':
                if (isInFinalAnalysis) {
                    return 'Generating final summary';
                }
                if (totalChunks) {
                    return `AI Analysis: Processing chunk ${currentChunk} of ${totalChunks} ${estimatedTime ? `(est. ${estimatedTime})` : ''}`;
                }
                return 'Starting AI processing';
            case 'complete':
                return 'AI Analysis complete';
            default:
                return 'Ready to process PDF';
        }
    }
</script>

<div class="flex flex-col items-center justify-center gap-4">
    <div class="border border-white p-8 w-[800px]">
        <div class="text-lg font-semibold text-white text-center mb-6">{message}</div>
        {#if status !== 'complete' && status !== ''}
            <div class="flex flex-col items-center justify-center gap-2">
                <div class="relative w-full h-[12px]">
                    <div bind:this={progressContainer} class="absolute inset-0"></div>
                </div>
                <div class="flex justify-between w-full text-sm mt-4">
                    <div class="text-white/70">
                        {#if status === 'analyzing'}
                            {#if isInFinalAnalysis}
                                Final Analysis
                            {:else}
                                Processing Document
                            {/if}
                        {:else if status === 'processing'}
                            OCR Analysis
                        {/if}
                    </div>
                    <div class="text-white">
                        {Math.round(progressPercent * 100)}%
                    </div>
                </div>
                {#if status === 'analyzing' && !isInFinalAnalysis}
                    <div class="text-white/50 text-xs mt-4">AI analysis in progress - this may take several minutes.</div>
                {/if}
            </div>
        {/if}
    </div>
</div>

<style>
    :global(.ldBar) {
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
    }
    :global(.ldBar svg) {
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
    }
    :global(.ldBar path.mainline, .ldBar path.baseline) {
        stroke-width: 24px !important;
    }
    :global(.ldBar path.baseline) {
        stroke: rgba(67, 67, 67, 0.85) !important;
    }
    :global(.ldBar-label) {
        display: none !important;
    }
</style>