document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const datasetSelect = document.getElementById('dataset-select');
    const fileUpload = document.getElementById('file-upload');
    const textContent = document.getElementById('text-content');
    const textOverlay = document.getElementById('text-overlay');
    const textLength = document.getElementById('text-length');
    const algoSelect = document.getElementById('algorithm-select');
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Results Elements
    const matchCount = document.getElementById('match-count');
    const timeTaken = document.getElementById('time-taken');
    const spaceUsed = document.getElementById('space-used');
    const statusMessage = document.getElementById('status-message');
    const matchesList = document.getElementById('matches-list');
    const metricsGrid = document.getElementById('metrics-grid');
    const comparisonTableContainer = document.getElementById('comparison-table-container');
    const comparisonBody = document.getElementById('comparison-body');

    // Trace Modal
    const traceModal = document.getElementById('trace-modal');
    const traceContainer = document.getElementById('trace-container');
    const closeModal = document.querySelector('.close');
    const tracePrev = document.getElementById('trace-prev');
    const traceNext = document.getElementById('trace-next');
    const tracePlay = document.getElementById('trace-play');

    // Chart
    let perfChart = null;
    const ctx = document.getElementById('perfChart').getContext('2d');

    // Initialize Chart
    function initChart() {
        perfChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Time (ms)', 'Space (KB)'],
                datasets: [{
                    label: 'Performance',
                    data: [0, 0],
                    backgroundColor: ['#3b82f6', '#10b981'],
                    borderColor: ['#3b82f6', '#10b981'],
                    borderWidth: 1,
                    barPercentage: 0.6,
                    categoryPercentage: 0.8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f1f5f9', font: { family: 'Inter', size: 12 } },
                        position: 'top',
                        align: 'end'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(148, 163, 184, 0.1)',
                        borderWidth: 1
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    }
                }
            }
        });
    }

    initChart();

    // Load Datasets
    fetch('/api/datasets')
        .then(res => res.json())
        .then(data => {
            datasetSelect.innerHTML = '';
            data.datasets.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                if (name === data.current) option.selected = true;
                datasetSelect.appendChild(option);
            });
            loadDataset(data.current);
        });

    // Event Listeners
    datasetSelect.addEventListener('change', (e) => loadDataset(e.target.value));

    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        fetch('/api/upload', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const option = document.createElement('option');
                    option.value = data.name;
                    option.textContent = data.name;
                    option.selected = true;
                    datasetSelect.appendChild(option);
                    loadDataset(data.name);
                } else {
                    alert('Upload failed: ' + data.error);
                }
            });
    });

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
        });
    });

    closeModal.onclick = () => traceModal.style.display = "none";
    window.onclick = (event) => { if (event.target == traceModal) traceModal.style.display = "none"; };

    // Helper Functions
    function loadDataset(name) {
        statusMessage.textContent = 'Loading dataset...';
        fetch('/api/dataset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        })
            .then(res => res.json())
            .then(data => {
                if (data.text) {
                    textContent.value = data.text;
                    textLength.textContent = data.text.length.toLocaleString();
                    statusMessage.textContent = `Loaded ${name}`;
                    highlightMatches([], data.text);
                }
            });
    }

    // FIXED: Improved highlighting function
    function highlightMatches(matches, text, patternLength = 1) {
        const textOverlay = document.getElementById('text-overlay');
        const textContentEl = document.getElementById('text-content');

        if (!matches || matches.length === 0) {
            textOverlay.innerHTML = '';
            textOverlay.classList.remove('active');
            textContentEl.classList.remove('has-overlay');
            return;
        }

        if (text.length > 50000) {
            textOverlay.innerHTML = '';
            textOverlay.classList.remove('active');
            textContentEl.classList.remove('has-overlay');
            return;
        }

        const isHighlighted = new Array(text.length).fill(false);

        matches.forEach(startIdx => {
            const endIdx = Math.min(startIdx + patternLength, text.length);
            for (let i = startIdx; i < endIdx; i++) {
                isHighlighted[i] = true;
            }
        });

        let html = '';
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            const escapedChar = char === '<' ? '&lt;' : char === '>' ? '&gt;' : char === '&' ? '&amp;' : char;

            if (isHighlighted[i]) {
                html += `<span class="highlight-match">${escapedChar}</span>`;
            } else {
                html += `<span>${escapedChar}</span>`;
            }
        }

        textOverlay.innerHTML = html;
        textOverlay.classList.add('active');
        textContentEl.classList.add('has-overlay');

        // Sync scroll positions
        textOverlay.scrollTop = textContentEl.scrollTop;
        textOverlay.scrollLeft = textContentEl.scrollLeft;
    }

    // Sync scroll between textarea and overlay
    textContent.addEventListener('scroll', () => {
        textOverlay.scrollTop = textContent.scrollTop;
        textOverlay.scrollLeft = textContent.scrollLeft;
    });

    window.runOperation = function (type) {
        const algo = algoSelect.value;
        const caseSensitiveCheckbox = document.getElementById('case-sensitive');
        const caseSensitive = caseSensitiveCheckbox ? caseSensitiveCheckbox.checked : false;
        let pattern = '';
        let insertText = '';

        console.log("=== OPERATION REQUEST ===");
        console.log("Type:", type);
        console.log("Algorithm:", algo);
        console.log("Case-sensitive checkbox:", caseSensitiveCheckbox);
        console.log("Case-sensitive value:", caseSensitive);
        console.log("========================");

        if (type === 'search') {
            pattern = document.getElementById('search-pattern').value;
        } else if (type === 'insert') {
            pattern = document.getElementById('insert-pattern').value;
            insertText = document.getElementById('insert-text').value;
        } else if (type === 'delete') {
            pattern = document.getElementById('delete-pattern').value;
        }

        if (!pattern) {
            alert('Please enter a pattern');
            return;
        }

        if (algo === 'All') {
            statusMessage.textContent = `Running ${type} with All Algorithms...`;
        } else {
            statusMessage.textContent = `Running ${type} with ${algo}...`;
        }

        fetch('/api/operation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: type,
                algorithm: algo,
                pattern: pattern,
                insert_text: insertText,
                case_sensitive: caseSensitive
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                if (Array.isArray(data)) {
                    handleComparisonResults(data, pattern.length);
                } else {
                    handleSingleResult(data, pattern.length);
                }
            })
            .catch(err => {
                console.error(err);
                statusMessage.textContent = 'Network error';
            });
    };

    function updateMatchesList(matches) {
        matchesList.innerHTML = '';
        if (matches && matches.length > 0) {
            const currentText = textContent.value;

            matches.slice(0, 50).forEach(idx => {
                const div = document.createElement('div');
                div.className = 'match-item clickable';

                const patternLength = document.getElementById('search-pattern')?.value.length ||
                    document.getElementById('insert-pattern')?.value.length ||
                    document.getElementById('delete-pattern')?.value.length || 1;
                const matchedString = currentText.substring(idx, idx + patternLength);

                div.innerHTML = `
                    <span style="color: var(--text-secondary);">Index ${idx}:</span> 
                    <span style="color: var(--success-color); font-weight: bold;">"${matchedString}"</span>
                `;
                div.onclick = () => window.scrollToMatch(idx);
                matchesList.appendChild(div);
            });

            if (matches.length > 50) {
                const div = document.createElement('div');
                div.className = 'match-item';
                div.textContent = `...and ${matches.length - 50} more`;
                matchesList.appendChild(div);
            }
        } else {
            matchesList.innerHTML = '<div class="match-item">No matches found</div>';
        }
    }

    // Find the runTrace function and update it to store truncation info
    // Replace the existing window.runTrace function with this:

    window.runTrace = function () {
        const pattern = document.getElementById('search-pattern').value;
        const algo = algoSelect.value;
        const caseSensitiveCheckbox = document.getElementById('case-sensitive');
        const caseSensitive = caseSensitiveCheckbox ? caseSensitiveCheckbox.checked : false;

        console.log("=== TRACE REQUEST ===");
        console.log("Pattern:", pattern);
        console.log("Algorithm:", algo);
        console.log("Case-sensitive checkbox element:", caseSensitiveCheckbox);
        console.log("Case-sensitive value:", caseSensitive);
        console.log("=====================");

        if (algo === 'All') {
            alert('Please select a specific algorithm for tracing');
            return;
        }
        if (!pattern) {
            alert('Enter a pattern');
            return;
        }

        statusMessage.textContent = 'Loading trace visualization...';

        fetch('/api/trace', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                algorithm: algo,
                pattern: pattern,
                case_sensitive: caseSensitive
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    statusMessage.textContent = 'Ready';
                    return;
                }

                console.log("=== TRACE DATA RECEIVED ===");
                console.log("Steps:", data.steps.length);
                console.log("Pattern:", data.pattern);
                console.log("Original Pattern:", data.original_pattern);
                console.log("Text (first 100):", data.text ? data.text.substring(0, 100) : "N/A");
                console.log("Original Text (first 100):", data.original_text ? data.original_text.substring(0, 100) : "N/A");
                console.log("Case Sensitive:", data.case_sensitive);
                console.log("===========================");

                traceSteps = data.steps;
                tracePattern = data.original_pattern || data.pattern;
                // CRITICAL: Always use original_text for display (has correct casing)
                traceText = data.original_text || data.text;
                traceAlgorithm = data.algorithm;
                traceCaseSensitive = data.case_sensitive || false;

                // ADDED: Store truncation info globally for renderTrace to use
                window.traceDataTruncated = data.truncated || false;
                window.traceOriginalLength = data.original_length || traceText.length;
                window.traceCaseSensitive = traceCaseSensitive;

                currentStep = 0;
                traceModal.style.display = 'block';
                renderTrace();
                statusMessage.textContent = 'Trace visualization ready';
            })
            .catch(err => {
                console.error(err);
                alert('Failed to load trace');
                statusMessage.textContent = 'Ready';
            });
    };

    function handleSingleResult(data, patternLength) {
        metricsGrid.style.display = 'grid';
        comparisonTableContainer.style.display = 'none';

        matchCount.textContent = data.match_count;
        timeTaken.textContent = (data.time_taken * 1000).toFixed(4);
        spaceUsed.textContent = (data.space_peak / 1024).toFixed(2);
        statusMessage.textContent = `Completed ${data.operation}`;

        // For all operations, update the text display
        if (data.updated_text) {
            textContent.value = data.updated_text;
            textLength.textContent = data.updated_text.length.toLocaleString();
        }

        updateMatchesList(data.matches);

        // Use the actual displayed text for highlighting
        const displayText = textContent.value;
        highlightMatches(data.matches, displayText, patternLength);

        if (perfChart.config.type !== 'bar') {
            perfChart.destroy();
            initChart();
        }

        perfChart.data.labels = ['Time (ms)', 'Space (KB)'];
        perfChart.data.datasets = [{
            label: data.algorithm,
            data: [data.time_taken * 1000, data.space_peak / 1024],
            backgroundColor: ['#3b82f6', '#10b981'],
            borderColor: ['#3b82f6', '#10b981'],
            borderWidth: 1
        }];
        perfChart.update();
    }

    function handleComparisonResults(results) {
        metricsGrid.style.display = 'none';
        comparisonTableContainer.style.display = 'block';

        comparisonBody.innerHTML = '';
        const labels = [];
        const timeData = [];
        const spaceData = [];

        results.forEach(res => {
            const row = `<tr>
                <td>${res.algorithm}</td>
                <td>${res.match_count}</td>
                <td>${(res.time_taken * 1000).toFixed(4)}</td>
                <td>${(res.space_peak / 1024).toFixed(2)}</td>
            </tr>`;
            comparisonBody.innerHTML += row;

            labels.push(res.algorithm);
            timeData.push(res.time_taken * 1000);
            spaceData.push(res.space_peak / 1024);
        });

        statusMessage.textContent = 'Comparison Complete';
        updateMatchesList(results[0].matches);

        if (perfChart.config.type !== 'bar') {
            perfChart.destroy();
            initChart();
        }

        perfChart.data.labels = labels;
        perfChart.data.datasets = [
            {
                label: 'Time (ms)',
                data: timeData,
                backgroundColor: '#3b82f6',
                borderColor: '#3b82f6',
                borderWidth: 1
            },
            {
                label: 'Space (KB)',
                data: spaceData,
                backgroundColor: '#10b981',
                borderColor: '#10b981',
                borderWidth: 1
            }
        ];
        perfChart.update();
    }

    window.scrollToMatch = function (index) {
        textContent.focus();
        textContent.setSelectionRange(index, index + 1);
        textContent.blur();
        textContent.focus();
    };

    window.runBulkSearch = function () {
        const fileInput = document.getElementById('bulk-file');
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('algorithm', algoSelect.value);

        statusMessage.textContent = 'Running Bulk Search...';

        fetch('/api/bulk_search', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                statusMessage.textContent = `Bulk Search: ${data.total_matches} matches in ${data.pattern_count} patterns`;
                matchesList.innerHTML = '';
                data.details.forEach(d => {
                    const div = document.createElement('div');
                    div.className = 'match-item';
                    div.textContent = `${d.pattern}: ${d.count} matches`;
                    matchesList.appendChild(div);
                });
            });
    };

    window.exportResults = function () {
        window.location.href = '/api/export';
    };

    window.generateDataset = function () {
        const type = document.getElementById('gen-type').value;
        const length = document.getElementById('gen-length').value;

        statusMessage.textContent = 'Generating dataset...';

        fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type, length: length })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const option = document.createElement('option');
                    option.value = data.name;
                    option.textContent = data.name;
                    option.selected = true;
                    datasetSelect.appendChild(option);

                    textContent.value = data.text;
                    textLength.textContent = data.text.length.toLocaleString();
                    statusMessage.textContent = `Generated ${data.name}`;
                    highlightMatches([], data.text);
                } else {
                    alert('Generation failed: ' + data.error);
                }
            });
    };

    window.runBenchmark = function () {
        const pattern = document.getElementById('bench-pattern').value;
        const maxLen = document.getElementById('bench-max').value;
        const step = document.getElementById('bench-step').value;
        const algo = algoSelect.value;

        if (!pattern) {
            alert('Pattern required');
            return;
        }

        statusMessage.textContent = `Running Benchmark for ${algo} (Length ${step} to ${maxLen})...`;

        fetch('/api/benchmark', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                algorithm: algo,
                pattern: pattern,
                max_length: maxLen,
                step: step
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                const datasets = [];
                let labels = [];

                const results = Array.isArray(data) ? data : [data];
                labels = results[0].data.map(d => d.length);

                const colors = ['#3b82f6', '#10b981', '#ef4444'];

                results.forEach((res, idx) => {
                    datasets.push({
                        label: res.algorithm,
                        data: res.data.map(d => d.time * 1000),
                        borderColor: colors[idx % colors.length],
                        backgroundColor: colors[idx % colors.length],
                        fill: false,
                        tension: 0.1
                    });
                });

                if (perfChart) perfChart.destroy();

                perfChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Time (ms)', color: '#94a3b8' },
                                grid: { color: 'rgba(148, 163, 184, 0.1)' },
                                ticks: { color: '#94a3b8' }
                            },
                            x: {
                                title: { display: true, text: 'Text Length', color: '#94a3b8' },
                                grid: { display: false },
                                ticks: { color: '#94a3b8' }
                            }
                        },
                        plugins: { legend: { labels: { color: '#f1f5f9' } } }
                    }
                });

                statusMessage.textContent = 'Benchmark Complete';
            });
    };

    // ENHANCED TRACE VISUALIZATION WITH MATCH COUNTER
    let traceSteps = [];
    let currentStep = 0;
    let traceTimer = null;
    let tracePattern = '';
    let traceText = '';
    let traceAlgorithm = '';
    let traceCaseSensitive = false;

    function renderTrace() {
        traceContainer.innerHTML = '';

        // Get algorithm name from steps
        const algoName = traceSteps.length > 0 ? traceSteps[0].description : '';

        // Count matches from trace steps
        let matchCount = 0;
        const matchPositions = [];
        traceSteps.forEach(step => {
            if (step.match && step.match_index !== undefined) {
                if (!matchPositions.includes(step.match_index)) {
                    matchPositions.push(step.match_index);
                    matchCount++;
                }
            }
        });

        // Create results summary header
        const resultsHeader = document.createElement('div');
        resultsHeader.className = 'trace-results-header';
        const caseSensitiveText = window.traceCaseSensitive ? '🔤 Case-sensitive search' : '🔍 Case-insensitive search';
        const matchText = matchCount === 1 ? '1 Match Found' : `${matchCount} Matches Found`;
        const patternText = matchCount === 1
            ? `Pattern "${tracePattern}" found 1 time in the text`
            : `Pattern "${tracePattern}" found ${matchCount} times in the text`;

        resultsHeader.innerHTML = `
        <div style="text-align: center; margin-bottom: 1.5rem; padding: 1rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%); border-radius: 0.75rem; border: 1px solid rgba(59, 130, 246, 0.3);">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯 Pattern Search Results</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: ${matchCount > 0 ? 'var(--success-color)' : 'var(--danger-color)'}; margin-bottom: 0.25rem;">
                ${matchText}
            </div>
            <div style="font-size: 1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                ${patternText}
            </div>
            <div style="font-size: 0.9rem; color: var(--accent-color);">
                ${caseSensitiveText}
            </div>
        </div>
    `;
        traceContainer.appendChild(resultsHeader);

        // Algorithm explanation based on type
        const algorithmExplanations = {
            'Finite Automata': `
            <strong>How it works:</strong> Builds a state machine with ${tracePattern.length + 1} states (0 to ${tracePattern.length}). 
            Each character read transitions between states. When state ${tracePattern.length} is reached, a match is found.
            <br><strong>Watch for:</strong> State transitions and when the final state is reached (green highlight).
        `,
            'Z-Algorithm': `
            <strong>How it works:</strong> Creates string "pattern$text" and computes Z-values (longest substring starting at each position that matches the prefix). 
            Uses Z-box optimization to avoid redundant comparisons.
            <br><strong>Watch for:</strong> When Z-value equals ${tracePattern.length} (pattern length), a match is found. Yellow shows comparison areas.
        `,
            'Bitap': `
            <strong>How it works:</strong> Uses bitwise operations with a bit vector representing pattern positions. 
            Each character shifts the vector and applies character masks. The MSB (leftmost bit) indicates a complete match.
            <br><strong>Watch for:</strong> Bit vectors updating (shown in binary) and when the MSB is set (match found).
        `
        };

        // Determine which algorithm
        let currentAlgo = 'Finite Automata';
        if (algoName.includes('Z-Algorithm')) currentAlgo = 'Z-Algorithm';
        if (algoName.includes('Bitap')) currentAlgo = 'Bitap';

        // Create pattern info with truncation warning if needed
        const patternInfo = document.createElement('div');
        patternInfo.className = 'trace-pattern-info';

        // Check if we have truncation info from the response
        const truncationWarning = window.traceDataTruncated
            ? `<br><span style="color: #fbbf24;">⚠️ Text truncated from ${window.traceOriginalLength.toLocaleString()} to ${traceText.length} characters for visualization</span>`
            : '';

        patternInfo.innerHTML = `
        <strong>Pattern:</strong> "${tracePattern}" (length: ${tracePattern.length})<br>
        <strong>Text Length:</strong> ${traceText.length} characters${truncationWarning}<br>
        <strong>Algorithm:</strong> ${currentAlgo}
    `;
        traceContainer.appendChild(patternInfo);

        // Add algorithm explanation
        const explanation = document.createElement('div');
        explanation.className = 'algorithm-explanation';
        explanation.innerHTML = algorithmExplanations[currentAlgo] || '';
        traceContainer.appendChild(explanation);

        // Create legend
        const legend = document.createElement('div');
        legend.className = 'trace-legend';
        legend.innerHTML = `
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; padding: 0.5rem; background: rgba(0,0,0,0.2); border-radius: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 20px; background: var(--accent-color); border-radius: 3px;"></span>
                <span style="font-size: 0.85rem;">Current Position</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 20px; background: rgba(251, 191, 36, 0.3); border: 1px solid #fbbf24; border-radius: 3px;"></span>
                <span style="font-size: 0.85rem;">Comparing</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 20px; background: var(--success-color); border-radius: 3px;"></span>
                <span style="font-size: 0.85rem;">Match Found</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 20px; background: rgba(16, 185, 129, 0.6); border: 1px solid var(--success-color); border-radius: 3px;"></span>
                <span style="font-size: 0.85rem;">Previous Match</span>
            </div>
        </div>
    `;
        traceContainer.appendChild(legend);

        // Create text display area
        const textDisplay = document.createElement('div');
        textDisplay.className = 'trace-text-display';
        textDisplay.id = 'trace-text-display';

        // Render each character
        for (let i = 0; i < traceText.length; i++) {
            const span = document.createElement('span');
            span.className = 'trace-char';
            span.textContent = traceText[i];
            span.id = `trace-char-${i}`;
            span.dataset.index = i;
            textDisplay.appendChild(span);
        }

        traceContainer.appendChild(textDisplay);

        // Create step info display
        const stepInfo = document.createElement('div');
        stepInfo.className = 'trace-step-info';
        stepInfo.id = 'trace-step-info';
        traceContainer.appendChild(stepInfo);

        updateTraceView();
    }

    function updateTraceView() {
        if (currentStep >= traceSteps.length) {
            currentStep = traceSteps.length - 1;
        }
        if (currentStep < 0) {
            currentStep = 0;
        }

        const step = traceSteps[currentStep];
        const stepInfo = document.getElementById('trace-step-info');

        // Reset all characters
        document.querySelectorAll('.trace-char').forEach(el => {
            el.className = 'trace-char';
        });

        if (stepInfo) {
            const stepNum = currentStep + 1;
            const totalSteps = traceSteps.length;
            const matchesUpToNow = traceSteps.slice(0, currentStep + 1).filter(s => s.match === true).length;

            stepInfo.innerHTML = `
                <div class="step-counter">Step ${stepNum} / ${totalSteps} | Matches found so far: ${matchesUpToNow}</div>
                <div class="step-description">${step.description || ''}</div>
                ${step.state_info ? `<div class="step-state">${step.state_info}</div>` : ''}
            `;
        }

        // Highlight current step
        if (step.highlight_ranges && step.highlight_ranges.length > 0) {
            step.highlight_ranges.forEach(range => {
                for (let i = range.start; i < range.end && i < traceText.length; i++) {
                    const el = document.getElementById(`trace-char-${i}`);
                    if (el) {
                        if (range.type === 'match') {
                            el.classList.add('trace-match');
                        } else if (range.type === 'current') {
                            el.classList.add('trace-current');
                        } else if (range.type === 'compare') {
                            el.classList.add('trace-compare');
                        }
                    }
                }
            });
        }

        // Keep all previous matches highlighted
        for (let i = 0; i <= currentStep; i++) {
            const prevStep = traceSteps[i];
            if (prevStep.match && prevStep.highlight_ranges) {
                prevStep.highlight_ranges.forEach(range => {
                    if (range.type === 'match') {
                        for (let j = range.start; j < range.end && j < traceText.length; j++) {
                            const el = document.getElementById(`trace-char-${j}`);
                            if (el && !el.classList.contains('trace-current') && !el.classList.contains('trace-match')) {
                                el.classList.add('trace-match-persistent');
                            }
                        }
                    }
                });
            }
        }

        statusMessage.textContent = step.description || `Step ${currentStep + 1}`;
    }

    tracePrev.onclick = () => {
        if (traceTimer) {
            clearInterval(traceTimer);
            traceTimer = null;
            tracePlay.textContent = 'Play';
        }
        if (currentStep > 0) {
            currentStep--;
            updateTraceView();
        }
    };

    traceNext.onclick = () => {
        if (traceTimer) {
            clearInterval(traceTimer);
            traceTimer = null;
            tracePlay.textContent = 'Play';
        }
        if (currentStep < traceSteps.length - 1) {
            currentStep++;
            updateTraceView();
        }
    };

    tracePlay.onclick = () => {
        if (traceTimer) {
            clearInterval(traceTimer);
            traceTimer = null;
            tracePlay.textContent = 'Play';
        } else {
            tracePlay.textContent = 'Pause';
            traceTimer = setInterval(() => {
                if (currentStep < traceSteps.length - 1) {
                    currentStep++;
                    updateTraceView();
                } else {
                    clearInterval(traceTimer);
                    traceTimer = null;
                    tracePlay.textContent = 'Play';
                }
            }, 500);
        }
    };

    document.addEventListener('keydown', (e) => {
        if (traceModal.style.display === 'block') {
            if (e.key === 'ArrowLeft') {
                tracePrev.click();
            } else if (e.key === 'ArrowRight') {
                traceNext.click();
            } else if (e.key === ' ') {
                e.preventDefault();
                tracePlay.click();
            } else if (e.key === 'Escape') {
                closeModal.click();
            }
        }
    });

});