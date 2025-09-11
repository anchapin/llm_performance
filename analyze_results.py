import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_and_plot(results_file="benchmark_results.csv"):
    """Loads benchmark results and creates visualizations."""
    
    try:
        df = pd.read_csv(results_file)
    except FileNotFoundError:
        print(f"Error: Results file '{results_file}' not found.")
        return

    sns.set_theme(style="whitegrid")

    # --- Figure 1: Speed vs. Accuracy Scatter Plot ---
    plt.figure(figsize=(14, 8))
    scatter_plot = sns.scatterplot(
        data=df[df['num_gpu'] == 999], # Plot only max GPU results for clarity
        x="tps",
        y="humaneval_pass@1",
        hue="model_base",
        style="quantization",
        s=200,
        alpha=0.8
    )
    plt.title("Performance Frontier: Speed vs. Accuracy (Max GPU Offload)", fontsize=16)
    plt.xlabel("Tokens per Second (TPS)", fontsize=12)
    plt.ylabel("HumanEval pass@1 (%)", fontsize=12)
    plt.legend(title="Configuration", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("figure1_speed_vs_accuracy.png")
    plt.show()

    # --- Figure 2: Impact of Quantization ---
    df_llama3_max_gpu = df[(df['model_base'] == 'llama3:8b-instruct') & (df['num_gpu'] == 999)]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df_llama3_max_gpu, x='quantization', y='tps', ax=ax1, color='skyblue', label='TPS')
    ax1.set_xlabel("Quantization", fontsize=12)
    ax1.set_ylabel("Tokens per Second (TPS)", fontsize=12, color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')

    ax2 = ax1.twinx()
    sns.lineplot(data=df_llama3_max_gpu, x='quantization', y='humaneval_pass@1', ax=ax2, color='red', marker='o', label='HumanEval pass@1')
    ax2.set_ylabel("HumanEval pass@1 (%)", fontsize=12, color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(bottom=df_llama3_max_gpu['humaneval_pass@1'].min() - 2)

    plt.title("Impact of Quantization on Speed and Accuracy (Llama3 8B, Max GPU)", fontsize=16)
    plt.tight_layout()
    plt.savefig("figure2_quantization_impact.png")
    plt.show()

    # --- Figure 3: Impact of GPU Offloading ---
    df_deepseek_q4 = df[(df['model_base'] == 'deepseek-coder:6.7b-instruct') & (df['quantization'] == 'q4_K_M')]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    # Determine the ordering of GPU layer categories present in the data.
    gpu_order = sorted(df_deepseek_q4['num_gpu'].unique())
    sns.barplot(data=df_deepseek_q4, x='num_gpu', y='tps', ax=ax1, color='lightgreen', order=gpu_order)
    ax1.set_xlabel("GPU Layers Offloaded", fontsize=12)
    ax1.set_ylabel("Tokens per Second (TPS)", fontsize=12, color='green')
    ax1.tick_params(axis='y', labelcolor='green')

    # Map to friendly labels only when there are exactly three categories; otherwise
    # fall back to the numeric values present in the dataset.
    if len(gpu_order) == 3:
        labels = ['CPU Only', 'Partial', 'Max GPU']
    else:
        labels = [str(v) for v in gpu_order]
    ax1.set_xticks(list(range(len(gpu_order))))
    ax1.set_xticklabels(labels)

    ax2 = ax1.twinx()
    sns.lineplot(data=df_deepseek_q4, x='num_gpu', y='avg_ttft_ms', ax=ax2, color='purple', marker='o')
    ax2.set_ylabel("Time to First Token (ms)", fontsize=12, color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')

    plt.title("Impact of GPU Offloading on Speed (DeepSeek Coder 6.7B Q4)", fontsize=16)
    plt.tight_layout()
    plt.savefig("figure3_gpu_offload_impact.png")
    plt.show()

if __name__ == "__main__":
    analyze_and_plot()