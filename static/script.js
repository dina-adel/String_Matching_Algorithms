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
                    backgroundColor: ['#3b82f6', '#10b981'], // Solid Blue, Solid Green
                    borderColor: ['#3b82f6', '#10b981'],
                    borderWidth: 1,
                    barPercentage: 0.6, // Make bars slightly thinner like the image
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
                        align: 'end' // Align legend to the right like the image
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
                    highlightMatches([], data.text); // Clear highlights
                }
            });
    }

    function highlightMatches(matches, text) {
        // Only highlight if text is small enough to avoid performance issues
        if (text.length > 20000) {
            textOverlay.innerHTML = '';
            return;
        }

        if (!matches || matches.length === 0) {
            textOverlay.textContent = text;
            return;
        }

        // Create a set for O(1) lookup
        const matchSet = new Set(matches);
        let html = '';
        // Simple highlighting (assumes single char matches or start indices)
        // For proper pattern highlighting we need pattern length.
        // This is a simplified version that just highlights the start index char
        // Improving to highlight full pattern would require passing pattern length

        // Let's just highlight the start index for now to be safe with overlaps
        for (let i = 0; i < text.length; i++) {
            if (matchSet.has(i)) {
                html += `<span class="highlight-match">${text[i]}</span>`;
            } else {
                html += text[i];
            }
        }
        textOverlay.innerHTML = html;
    }

    window.runOperation = function (type) {
        const algo = algoSelect.value;
        let pattern = '';
        let insertText = '';

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
                insert_text: insertText
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                if (Array.isArray(data)) {
                    // Handle Compare All
                    handleComparisonResults(data);
                } else {
                    // Handle Single Result
                    handleSingleResult(data);
                }
            })
            .catch(err => {
                console.error(err);
                statusMessage.textContent = 'Network error';
            });
    };

    function handleSingleResult(data) {
        metricsGrid.style.display = 'grid';
        comparisonTableContainer.style.display = 'none';

        matchCount.textContent = data.match_count;
        timeTaken.textContent = (data.time_taken * 1000).toFixed(4);
        spaceUsed.textContent = (data.space_peak / 1024).toFixed(2);
        statusMessage.textContent = `Completed ${data.operation}`;

        if (data.updated_text) {
            textContent.value = data.updated_text;
            textLength.textContent = data.updated_text.length.toLocaleString();
        }

        updateMatchesList(data.matches);
        highlightMatches(data.matches, textContent.value);

        // Update Chart
        // Reset chart to bar type if it was line
        if (perfChart.config.type !== 'bar') {
            perfChart.destroy();
            initChart();
        }

        perfChart.data.labels = ['Time (ms)', 'Space (KB)'];
        perfChart.data.datasets = [{
            label: data.algorithm,
            data: [data.time_taken * 1000, data.space_peak / 1024],
            backgroundColor: ['#3b82f6', '#10b981'], // Solid Blue, Solid Green
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
        updateMatchesList(results[0].matches); // Show matches from first algo

        // Update Chart for Comparison
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

    // Scroll Sync
    textContent.addEventListener('scroll', () => {
        textOverlay.scrollTop = textContent.scrollTop;
    });

    window.scrollToMatch = function (index) {
        textContent.focus();
        textContent.setSelectionRange(index, index + 1);
        // Trigger scroll by focusing
        textContent.blur();
        textContent.focus();
    };

    function updateMatchesList(matches) {
        matchesList.innerHTML = '';
        if (matches && matches.length > 0) {
            matches.slice(0, 50).forEach(idx => {
                const div = document.createElement('div');
                div.className = 'match-item clickable';
                div.textContent = `Index: ${idx}`;
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

    // Trace Logic
    let traceSteps = [];
    let currentStep = 0;
    let traceTimer = null;

    window.runTrace = function () {
        const pattern = document.getElementById('search-pattern').value;
        const algo = algoSelect.value;

        if (algo === 'All') {
            alert('Please select a specific algorithm for tracing');
            return;
        }
        if (!pattern) {
            alert('Enter a pattern');
            return;
        }

        fetch('/api/trace', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ algorithm: algo, pattern: pattern })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                traceSteps = data.steps;
                currentStep = 0;
                traceModal.style.display = 'block';
                renderTrace();
            });
    };

    function renderTrace() {
        traceContainer.innerHTML = '';
        // Assuming we are tracing the first 100 chars
        const text = textContent.value.substring(0, 100);

        for (let i = 0; i < text.length; i++) {
            const span = document.createElement('span');
            span.className = 'trace-char';
            span.textContent = text[i];
            span.id = `trace-char-${i}`;
            traceContainer.appendChild(span);
        }

        updateTraceView();
    }

    function updateTraceView() {
        if (currentStep >= traceSteps.length) return;

        const step = traceSteps[currentStep];

        // Reset styles
        document.querySelectorAll('.trace-char').forEach(el => el.className = 'trace-char');

        // Highlight current
        if (step.index !== undefined) {
            const el = document.getElementById(`trace-char-${step.index}`);
            if (el) {
                el.classList.add('active');
                if (step.match) {
                    el.classList.add('match-found');
                }
            }
        }

        statusMessage.textContent = `Step ${currentStep + 1}: ${step.description}`;
    }

    traceNext.onclick = () => {
        if (currentStep < traceSteps.length - 1) {
            currentStep++;
            updateTraceView();
        }
    };

    tracePrev.onclick = () => {
        if (currentStep > 0) {
            currentStep--;
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
            }, 200);
        }
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

                // Render Line Chart
                const datasets = [];
                let labels = [];

                // Data can be a single result obj or list of result objs
                const results = Array.isArray(data) ? data : [data];

                // Use labels from the first result
                labels = results[0].data.map(d => d.length);

                const colors = ['#3b82f6', '#10b981', '#ef4444'];

                results.forEach((res, idx) => {
                    datasets.push({
                        label: res.algorithm,
                        data: res.data.map(d => d.time * 1000), // ms
                        borderColor: colors[idx % colors.length],
                        backgroundColor: colors[idx % colors.length],
                        fill: false,
                        tension: 0.1
                    });
                });

                // Destroy old chart if it was bar, or just update
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
});
