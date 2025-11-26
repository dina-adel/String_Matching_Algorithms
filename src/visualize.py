"""
Comprehensive Results Visualizer
Reads benchmark_results.json and creates publication-quality visualizations
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import seaborn as sns

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ResultsVisualizer:
    """Visualize benchmark results from JSON file."""
    
    def __init__(self, json_file: str = "results/benchmark_results.json", 
                 output_dir: str = "results/plots"):
        self.json_file = Path(json_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        with open(self.json_file, 'r') as f:
            self.results = json.load(f)
        
        print(f"✓ Loaded {len(self.results)} benchmark results from {self.json_file}")
        
        # Color scheme
        self.colors = {
            'Bitap': '#E63946',           # Red
            'Finite Automata': '#457B9D', # Blue
            'Z-Algorithm': '#2A9D8F'      # Teal
        }
    
    def generate_all_plots(self):
        """Generate all visualization plots for each dataset type."""
        print("\n" + "="*70)
        print("GENERATING ALL VISUALIZATIONS")
        print("="*70)
        
        # Identify all dataset types
        dataset_types = sorted(list(set(r['dataset_type'] for r in self.results)))
        print(f"Found datasets: {', '.join(dataset_types)}")
        
        for dtype in dataset_types:
            print(f"\nProcessing dataset: {dtype}")
            print("-" * 40)
            
            # Create subdirectory for this dataset
            dtype_dir = self.output_dir / dtype
            dtype_dir.mkdir(parents=True, exist_ok=True)
            
            self.plot_time_scaling_by_text_size(dtype, dtype_dir)
            self.plot_algorithm_comparison_bar(dtype, dtype_dir)
            self.plot_preprocessing_vs_search(dtype, dtype_dir)
            self.plot_memory_scaling(dtype, dtype_dir)
            self.plot_time_vs_pattern_length(dtype, dtype_dir)
            self.plot_throughput_analysis(dtype, dtype_dir)
            self.plot_speedup_comparison(dtype, dtype_dir)
            self.plot_time_memory_tradeoff(dtype, dtype_dir)
            self.plot_pattern_analysis(dtype, dtype_dir)
            self.generate_pattern_table(dtype, dtype_dir)
        
        print("\n" + "="*70)
        print("ALL VISUALIZATIONS COMPLETE")
        print(f"Plots saved to: {self.output_dir}")
        print("="*70)
    
    def plot_time_scaling_by_text_size(self, dataset_type, output_dir):
        """Plot: Total time vs text size (log-log) for each algorithm."""
        print(f"  Creating: Time Scaling by Text Size ({dataset_type})...")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Filter results for this dataset
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        # Group by algorithm
        for algo in ['Finite Automata', 'Z-Algorithm', 'Bitap']:
            algo_results = [r for r in dataset_results if r['algorithm'] == algo]
            
            if not algo_results: continue

            # Group by text size and compute average
            size_groups = defaultdict(list)
            for r in algo_results:
                size_groups[r['text_size']].append(r['time_ms'])
            
            sizes = sorted(size_groups.keys())
            avg_times = [np.mean(size_groups[s]) for s in sizes]
            std_times = [np.std(size_groups[s]) if len(size_groups[s]) > 1 else 0 
                        for s in sizes]
            
            ax.errorbar(sizes, avg_times, yerr=std_times, 
                       marker='o', label=algo, linewidth=2.5, markersize=9,
                       capsize=5, color=self.colors[algo], alpha=0.85)
        
        ax.set_xlabel('Text Size (characters)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Time (ms)', fontsize=13, fontweight='bold')
        ax.set_title(f'Execution Time vs Text Size ({dataset_type})', 
                    fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3, which='both', linestyle='--')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'time_scaling.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: time_scaling.png")
        plt.close()
    
    def plot_algorithm_comparison_bar(self, dataset_type, output_dir):
        """Plot: Bar chart comparing average times by text size."""
        print(f"  Creating: Algorithm Comparison Bar Chart ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        # Get unique text sizes
        text_sizes = sorted(set(r['text_size'] for r in dataset_results))
        algorithms = ['Finite Automata', 'Z-Algorithm', 'Bitap']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(text_sizes))
        width = 0.25
        
        for i, algo in enumerate(algorithms):
            avgs = []
            for size in text_sizes:
                times = [r['time_ms'] for r in dataset_results 
                        if r['algorithm'] == algo and r['text_size'] == size]
                avgs.append(np.mean(times) if times else 0)
            
            offset = (i - 1) * width
            bars = ax.bar(x + offset, avgs, width, label=algo, 
                         color=self.colors[algo], alpha=0.85)
            
            # Add value labels on bars for smaller values
            for j, (bar, val) in enumerate(zip(bars, avgs)):
                if val < 10000:  # Only label smaller values
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{val:.0f}', ha='center', va='bottom', fontsize=8)
        
        # Format x-axis labels
        size_labels = [f'{s//1000}K' if s < 1000000 else f'{s//1000000}M' 
                      for s in text_sizes]
        ax.set_xticks(x)
        ax.set_xticklabels(size_labels, fontsize=11)
        ax.set_xlabel('Text Size', fontsize=13, fontweight='bold')
        ax.set_ylabel('Average Time (ms)', fontsize=13, fontweight='bold')
        ax.set_title(f'Algorithm Performance Comparison by Text Size ({dataset_type})', 
                    fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y', which='both')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'algorithm_comparison.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: algorithm_comparison.png")
        plt.close()
    
    def plot_preprocessing_vs_search(self, dataset_type, output_dir):
        """Plot: Preprocessing vs Search time breakdown."""
        print(f"  Creating: Preprocessing vs Search Time ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        algorithms = ['Finite Automata', 'Z-Algorithm', 'Bitap']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Calculate average preprocessing and search times
        prep_times = []
        search_times = []
        
        for algo in algorithms:
            algo_results = [r for r in dataset_results if r['algorithm'] == algo]
            if not algo_results:
                prep_times.append(0)
                search_times.append(0)
                continue
                
            avg_prep = np.mean([r.get('preprocessing_time_ms', 0) for r in algo_results])
            avg_search = np.mean([r.get('search_time_ms', 0) for r in algo_results])
            prep_times.append(avg_prep)
            search_times.append(avg_search)
        
        x = np.arange(len(algorithms))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, prep_times, width, label='Preprocessing',
                      color='#457B9D', alpha=0.85)
        bars2 = ax.bar(x + width/2, search_times, width, label='Search',
                      color='#E63946', alpha=0.85)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        ax.set_ylabel('Time (ms)', fontsize=13, fontweight='bold')
        ax.set_title(f'Preprocessing vs Search Time ({dataset_type})', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, fontsize=11)
        ax.set_yscale('log')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y', which='both')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'preprocessing_vs_search.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: preprocessing_vs_search.png")
        plt.close()
    
    def plot_memory_scaling(self, dataset_type, output_dir):
        """Plot: Memory usage vs text size."""
        print(f"  Creating: Memory Scaling ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo in ['Finite Automata', 'Z-Algorithm', 'Bitap']:
            algo_results = [r for r in dataset_results if r['algorithm'] == algo]
            
            # Group by text size
            size_groups = defaultdict(list)
            for r in algo_results:
                size_groups[r['text_size']].append(r.get('memory_peak_kb', 0))
            
            sizes = sorted(size_groups.keys())
            avg_memory = [np.mean(size_groups[s]) for s in sizes]
            
            ax.plot(sizes, avg_memory, marker='o', label=algo,
                   linewidth=2.5, markersize=9, color=self.colors[algo], alpha=0.85)
        
        ax.set_xlabel('Text Size (characters)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Peak Memory (KB)', fontsize=13, fontweight='bold')
        ax.set_title(f'Memory Usage vs Text Size ({dataset_type})', fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, which='both', linestyle='--')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'memory_scaling.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: memory_scaling.png")
        plt.close()
    
    def plot_time_vs_pattern_length(self, dataset_type, output_dir):
        """Plot: Time vs pattern length - Separated by text size."""
        print(f"  Creating: Time vs Pattern Length ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        # Get unique text sizes
        text_sizes = sorted(set(r['text_size'] for r in dataset_results))
        
        # Create subplots for different text sizes
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()
        
        for idx, text_size in enumerate(text_sizes[:6]):  # Max 6 subplots
            ax = axes[idx]
            
            for algo in ['Finite Automata', 'Z-Algorithm', 'Bitap']:
                # Filter by algorithm AND text size
                filtered = [r for r in dataset_results 
                           if r['algorithm'] == algo and r['text_size'] == text_size]
                
                if not filtered:
                    continue
                
                # Sort by pattern length
                filtered.sort(key=lambda x: x['pattern_length'])
                
                lengths = [r['pattern_length'] for r in filtered]
                times = [r['time_ms'] for r in filtered]
                
                ax.plot(lengths, times, marker='o', label=algo,
                       linewidth=2, markersize=7, color=self.colors[algo], alpha=0.85)
            
            # Format
            size_label = f'{text_size//1000}K' if text_size < 1000000 else f'{text_size//1000000}M'
            ax.set_title(f'Text Size: {size_label}', fontsize=11, fontweight='bold')
            ax.set_xlabel('Pattern Length', fontsize=10)
            ax.set_ylabel('Time (ms)', fontsize=10)
            ax.set_yscale('log')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3, which='both', linestyle='--')
        
        # Hide unused subplots
        for idx in range(len(text_sizes), 6):
            axes[idx].axis('off')
        
        plt.suptitle(f'Execution Time vs Pattern Length ({dataset_type})', 
                    fontsize=15, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        plt.savefig(output_dir / 'time_vs_pattern_length.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: time_vs_pattern_length.png")
        plt.close()
    
    def plot_throughput_analysis(self, dataset_type, output_dir):
        """Plot: Throughput (MB/s) analysis."""
        print(f"  Creating: Throughput Analysis ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo in ['Finite Automata', 'Z-Algorithm', 'Bitap']:
            algo_results = [r for r in dataset_results if r['algorithm'] == algo]
            
            # Calculate throughput for each result
            size_groups = defaultdict(list)
            for r in algo_results:
                if r['time_ms'] > 0:
                    throughput = (r['text_size'] / (1024**2)) / (r['time_ms'] / 1000)
                    size_groups[r['text_size']].append(throughput)
            
            sizes = sorted(size_groups.keys())
            avg_throughput = [np.mean(size_groups[s]) for s in sizes]
            
            ax.plot(sizes, avg_throughput, marker='d', label=algo,
                   linewidth=2.5, markersize=8, color=self.colors[algo], alpha=0.85)
        
        ax.set_xlabel('Text Size (characters)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Throughput (MB/s)', fontsize=13, fontweight='bold')
        ax.set_title(f'Processing Throughput vs Text Size ({dataset_type})', fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3, which='both', linestyle='--')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'throughput.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: throughput.png")
        plt.close()
    
    def plot_speedup_comparison(self, dataset_type, output_dir):
        """Plot: Speedup comparison (relative to slowest algorithm)."""
        print(f"  Creating: Speedup Comparison ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        text_sizes = sorted(set(r['text_size'] for r in dataset_results))
        algorithms = ['Finite Automata', 'Z-Algorithm', 'Bitap']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for algo in algorithms:
            speedups = []
            for size in text_sizes:
                # Get average times for all algorithms at this size
                times = {}
                for a in algorithms:
                    a_times = [r['time_ms'] for r in dataset_results
                              if r['algorithm'] == a and r['text_size'] == size]
                    times[a] = np.mean(a_times) if a_times else float('inf')
                
                # Calculate speedup relative to slowest
                slowest = max(times.values())
                speedup = slowest / times[algo] if times[algo] > 0 else 0
                speedups.append(speedup)
            
            ax.plot(text_sizes, speedups, marker='o', label=algo,
                   linewidth=2.5, markersize=9, color=self.colors[algo], alpha=0.85)
        
        ax.set_xlabel('Text Size (characters)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Speedup (relative to slowest)', fontsize=13, fontweight='bold')
        ax.set_title(f'Relative Speedup Comparison ({dataset_type})', fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, linewidth=2)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, which='both', linestyle='--')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'speedup_comparison.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: speedup_comparison.png")
        plt.close()
    
    def plot_time_memory_tradeoff(self, dataset_type, output_dir):
        """Plot: Time vs Memory scatter plot showing trade-offs."""
        print(f"  Creating: Time-Memory Tradeoff ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        for algo in ['Finite Automata', 'Z-Algorithm', 'Bitap']:
            algo_results = [r for r in dataset_results if r['algorithm'] == algo]
            
            times = [r['time_ms'] for r in algo_results]
            memories = [r.get('memory_peak_kb', 0) for r in algo_results]
            sizes = [r['text_size'] for r in algo_results]
            
            # Scatter with size encoding
            ax.scatter(memories, times, s=[s/50000 for s in sizes],
                               alpha=0.6, label=algo, color=self.colors[algo])
        
        ax.set_xlabel('Peak Memory (KB)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Time (ms)', fontsize=13, fontweight='bold')
        ax.set_title(f'Time vs Memory Trade-off ({dataset_type})\n(bubble size = text size)', 
                    fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3, which='both', linestyle='--')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'time_memory_tradeoff.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: time_memory_tradeoff.png")
        plt.close()

    def plot_pattern_analysis(self, dataset_type, output_dir):
        """
        Plot 4-panel analysis of pattern characteristics:
        1. Pattern Length Dist
        2. Matches vs Time
        3. Length Category Impact
        4. Complexity Impact
        """
        print(f"  Creating: Pattern Analysis 4-Panel ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Data Preparation
        lengths = [r['pattern_length'] for r in dataset_results]
        matches = [r.get('matches_found', 0) for r in dataset_results]
        times = [r['time_ms'] for r in dataset_results]
        algos = [r['algorithm'] for r in dataset_results]
        patterns = [r['pattern'] for r in dataset_results]
        
        # 1. Histogram of Pattern Lengths
        ax1.hist(lengths, bins=15, color='#2A9D8F', alpha=0.7, edgecolor='black')
        ax1.set_title("Distribution of Pattern Lengths Tested", fontweight='bold')
        ax1.set_xlabel("Pattern Length")
        ax1.set_ylabel("Frequency")
        
        # 2. Scatter: Match Count vs Time (Color by Algo)
        for algo in self.colors:
            mask = [a == algo for a in algos]
            ax2.scatter(
                [m for m, is_a in zip(matches, mask) if is_a], 
                [t for t, is_a in zip(times, mask) if is_a],
                label=algo, color=self.colors[algo], alpha=0.6
            )
        ax2.set_title("Impact of Match Frequency on Time", fontweight='bold')
        ax2.set_xlabel("Number of Matches Found")
        ax2.set_ylabel("Time (ms)")
        ax2.set_yscale('log')
        ax2.legend()
        
        # 3. Bar: Short/Medium/Long Categories
        categories = {'Short (<5)': [], 'Medium (5-10)': [], 'Long (>10)': []}
        for r in dataset_results:
            cat = 'Short (<5)' if r['pattern_length'] < 5 else \
                  'Medium (5-10)' if r['pattern_length'] <= 10 else 'Long (>10)'
            categories[cat].append(r['time_ms'])
            
        cat_names = list(categories.keys())
        cat_avgs = [np.mean(categories[c]) if categories[c] else 0 for c in cat_names]
        ax3.bar(cat_names, cat_avgs, color=['#457B9D', '#2A9D8F', '#E63946'])
        ax3.set_title("Average Execution Time by Pattern Category", fontweight='bold')
        ax3.set_ylabel("Avg Time (ms)")
        
        # 4. Scatter: Pattern Complexity (Unique Chars / Length) vs Time
        complexity = [len(set(p))/len(p) for p in patterns]
        sc = ax4.scatter(complexity, times, c=[len(p) for p in patterns], cmap='viridis', alpha=0.6)
        plt.colorbar(sc, ax=ax4, label='Pattern Length')
        ax4.set_title("Pattern Complexity vs Time", fontweight='bold')
        ax4.set_xlabel("Complexity Ratio (Unique Chars / Length)")
        ax4.set_ylabel("Time (ms)")
        ax4.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'pattern_analysis.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: pattern_analysis.png")
        plt.close()

    def generate_pattern_table(self, dataset_type, output_dir):
        """
        Generate a detailed table comparing algorithms for every pattern tested.
        Saves as both a text file and a PNG image.
        """
        print(f"  Creating: Pattern Details Table ({dataset_type})...")
        
        dataset_results = [r for r in self.results if r['dataset_type'] == dataset_type]
        
        # Group results by (text_size, pattern)
        # Key: (size, pattern), Value: {algo: time, meta: {len, matches}}
        grouped = defaultdict(dict)
        
        for r in dataset_results:
            key = (r['text_size'], r['pattern'])
            # Store algorithm time
            grouped[key][r['algorithm']] = r['time_ms']
            # Store metadata (ensure we have it)
            grouped[key]['len'] = r['pattern_length']
            grouped[key]['matches'] = r.get('matches_found', -1) # -1 if not captured
            
        # Prepare rows for sorting
        rows = []
        for (size, pat), data in grouped.items():
            fa_time = data.get('Finite Automata', float('inf'))
            z_time = data.get('Z-Algorithm', float('inf'))
            bitap_time = data.get('Bitap', float('inf'))
            
            # Determine winner
            times = {'FA': fa_time, 'Z': z_time, 'Bitap': bitap_time}
            # Filter out infinite/failed
            valid_times = {k: v for k, v in times.items() if v != float('inf')}
            winner = min(valid_times, key=valid_times.get) if valid_times else "N/A"
            
            rows.append({
                'size': size,
                'pattern': pat,
                'len': data['len'],
                'matches': data['matches'],
                'FA': fa_time,
                'Z': z_time,
                'Bitap': bitap_time,
                'Winner': winner
            })
            
        # Sort by size then pattern length
        rows.sort(key=lambda x: (x['size'], x['len']))
        
        # 1. Generate Text File
        txt_path = output_dir / 'pattern_details.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            # Header
            header = f"{'Size':<10} | {'Pattern':<20} | {'Len':<5} | {'Matches':<8} | {'FA (ms)':<12} | {'Z-Algo (ms)':<12} | {'Bitap (ms)':<12} | {'Best'}"
            f.write(header + "\n")
            f.write("-" * len(header) + "\n")
            
            for row in rows:
                # Truncate pattern for display
                p_disp = (row['pattern'][:17] + '..') if len(row['pattern']) > 19 else row['pattern']
                p_disp = p_disp.replace('\n', '\\n')
                
                line = f"{row['size']:<10} | {p_disp:<20} | {row['len']:<5} | {row['matches']:<8} | {row['FA']:<12.2f} | {row['Z']:<12.2f} | {row['Bitap']:<12.2f} | {row['Winner']}"
                f.write(line + "\n")
        
        print(f"    ✓ Saved: {txt_path}")
        
        # 2. Generate Image (Simplified version of top 15 or representative rows if too large)
        # Because plotting a table of 1000 rows is impossible, we plot a summary or top 20
        display_rows = rows[:25] # Take first 25 for the image
        
        fig, ax = plt.subplots(figsize=(14, len(display_rows) * 0.5 + 2))
        ax.axis('off')
        ax.set_title(f"Pattern Performance Details ({dataset_type})", fontweight='bold', fontsize=14)
        
        table_data = []
        # Columns
        cols = ['Size', 'Pattern', 'Len', 'Matches', 'FA (ms)', 'Z (ms)', 'Bitap (ms)', 'Best']
        
        cell_colors = []
        
        for row in display_rows:
            p_disp = (row['pattern'][:15] + '..') if len(row['pattern']) > 15 else row['pattern']
            p_disp = p_disp.replace('\n', '\\n')
            
            r_data = [
                str(row['size']), p_disp, str(row['len']), str(row['matches']),
                f"{row['FA']:.2f}", f"{row['Z']:.2f}", f"{row['Bitap']:.2f}", row['Winner']
            ]
            table_data.append(r_data)
            
            # Color logic: Green for winner column
            row_colors = ['white'] * 8
            if row['Winner'] == 'FA': row_colors[4] = '#d1e7dd' # Light Green
            if row['Winner'] == 'Z':  row_colors[5] = '#d1e7dd'
            if row['Winner'] == 'Bitap': row_colors[6] = '#d1e7dd'
            row_colors[7] = '#d1e7dd'
            cell_colors.append(row_colors)

        tab = ax.table(cellText=table_data, colLabels=cols, cellColours=cell_colors,
                       loc='center', cellLoc='center')
        
        tab.auto_set_font_size(False)
        tab.set_fontsize(10)
        tab.scale(1, 1.5)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'pattern_table.png', dpi=300, bbox_inches='tight')
        print("    ✓ Saved: pattern_table.png")
        plt.close()
        
    def generate_summary_table(self):
        """Generate a summary table of results."""
        print("\n  Creating: Summary Statistics Table...")
        
        algorithms = ['Finite Automata', 'Z-Algorithm', 'Bitap']
        
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        
        for algo in algorithms:
            algo_results = [r for r in self.results if r['algorithm'] == algo]
            
            times = [r['time_ms'] for r in algo_results]
            memories = [r.get('memory_peak_kb', 0) for r in algo_results]
            
            print(f"\n{algo}:")
            print(f"  Time (ms):")
            print(f"    Mean:   {np.mean(times):>12.2f}")
            print(f"    Median: {np.median(times):>12.2f}")
            print(f"    Std:    {np.std(times):>12.2f}")
            print(f"    Min:    {np.min(times):>12.2f}")
            print(f"    Max:    {np.max(times):>12.2f}")
            
            print(f"  Memory (KB):")
            print(f"    Mean:   {np.mean(memories):>12.2f}")
            print(f"    Median: {np.median(memories):>12.2f}")
            print(f"    Std:    {np.std(memories):>12.2f}")
            print(f"    Min:    {np.min(memories):>12.2f}")
            print(f"    Max:    {np.max(memories):>12.2f}")
        
        print("\n" + "="*80)


def main():
    """Main function to generate all visualizations."""
    import sys
    
    # Check if file exists
    json_file = "results/benchmark_results.json"
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"❌ Error: File '{json_file}' not found!")
        print(f"   Usage: python {sys.argv[0]} [path_to_json_file]")
        return
    
    # Create visualizer and generate plots
    visualizer = ResultsVisualizer(json_file, output_dir="results/plots")
    visualizer.generate_all_plots()
    visualizer.generate_summary_table()
    
    print(f"\n✅ All visualizations complete!")
    print(f"📁 Check the '{visualizer.output_dir}' directory for all plots.")


if __name__ == "__main__":
    main()