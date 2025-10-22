import os
import itertools
import statistics
import pandas as pd
import dat1


def calculate_all_combinations_dat(model, words):
    """Calculate DAT scores for ALL possible combinations of 7 words from valid words"""
    # Filter out empty/NaN values and convert to list of strings
    word_list = [str(word).strip() for word in words if pd.notna(word) and str(word).strip()]
    
    if len(word_list) == 0:
        return {}, 0, [], []

    # Helper function to convert umlauts
    def convert_umlauts(word):
        """Convert German umlauts to ae, oe, ue equivalents"""
        return word.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue')

    # Check words and collect valid ones (keep order), also track invalid ones
    valid_words = []
    invalid_words = []
    for word in word_list:
        validated = model.validate(word)
        if validated is not None:
            valid_words.append(validated)
        else:
            # Try with umlauts converted if the word contains umlauts
            if any(char in word for char in ['ä', 'ö', 'ü', 'Ä', 'Ö', 'Ü']):
                converted_word = convert_umlauts(word)
                validated_converted = model.validate(converted_word)
                if validated_converted is not None:
                    valid_words.append(validated_converted)
                    print(f"Converted '{word}' to '{converted_word}' - now valid")
                else:
                    invalid_words.append(word)
            else:
                invalid_words.append(word)

    # Return empty dict if less than 7 valid words
    if len(valid_words) < 7:
        return {}, len(valid_words), valid_words, invalid_words

    # Generate all possible combinations of 7 words
    all_combinations = list(itertools.combinations(valid_words, 7))

    results = {}

    # Calculate DAT score for each combination
    for i, combo in enumerate(all_combinations):
       score = model.dat(list(combo))

    # Special naming for first and last combinations
    if i == 0:  # First 7 words (same as original first7)
        results['DAT_first7'] = score
    elif i == len(all_combinations) - 1:  # Last combination
        results['DAT_last7'] = score
    else:
        # Name other combinations as combi_1, combi_2, etc.
        combo_num = i  # Will be 1, 2, 3... (skipping 0 for first7)
        if combo_num > len(all_combinations) - 2:  # Adjust for last7
            combo_num -= 1
        results[f'combi_{combo_num}'] = score

    return results, len(valid_words), valid_words, invalid_words


def calculate_stability_metrics(dat_scores):
    """Calculate comprehensive stability metrics for psychology research"""
    if len(dat_scores) < 2:
        return {}

    # Filter out None values from scores
    scores = [score for score in dat_scores.values() if score is not None]

    if len(scores) < 2:
        return {}

    # Basic descriptive statistics
    mean_score = statistics.mean(scores)
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
    min_score = min(scores)
    max_score = max(scores)
    range_score = max_score - min_score

    return {
        'n_combinations': len(scores),
        'mean': mean_score,
        'std_dev': std_dev,
        'min': min_score,
        'max': max_score,
        'range': range_score,
    }

def process_dat_responses():
    """Process the Excel file and calculate DAT scores for all participants with comprehensive stability analysis"""
    print("Loading model... This may take several minutes due to large file size...")

    # Load the model
    model = dat1.Model("model/vectors.txt", "model/vocab.txt")
    print("Model loaded successfully!")

    # Read the data
    input_file = "data/dat.xlsx"
    csv_file = "data/dat.csv"

    # Try to read Excel file first, fall back to CSV if needed
    try:
        if os.path.exists(input_file):
            df = pd.read_excel(input_file)
        elif os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
        else:
            raise FileNotFoundError("data file not found")
    except Exception as e:
        print(f"Error reading data file: {e}")
        return

    print(f"Data loaded: {len(df)} participants")

    # Prepare results dataframes
    basic_results = []
    stability_results = []
    all_combinations_results = []
    invalid_words_results = []

    # Process each participant
    for index, row in df.iterrows():
        participant_id = row['vpn']  # First column is participant ID

        # Extract the 10 word responses (dat_eingabe_1 to dat_eingabe_10)
        word_columns = [f'dat_eingabe_{i}' for i in range(1, 11)]
        words = [row[col] for col in word_columns if col in df.columns]

        # Calculate all possible DAT combinations
        all_dat_scores, valid_count, valid_words, invalid_words = calculate_all_combinations_dat(model, words)

        # Track invalid words for this participant
        for word in invalid_words:
            invalid_words_results.append({
                'participant_id': participant_id,
                'invalid_word': word
            })

        # Also track empty/missing words
        original_words = [row[col] for col in word_columns if col in df.columns]
        for i, word in enumerate(original_words, 1):
            if pd.isna(word) or str(word).strip() == '':
                invalid_words_results.append({
                    'participant_id': participant_id,
                    'invalid_word': f'[Empty/Missing in position {i}]',
                    'reason': 'Empty or missing'
                })

        # Filter out None values for stability analysis
        valid_dat_scores = {k: v for k, v in all_dat_scores.items() if v is not None}

        if len(valid_dat_scores) >= 2:  # Need at least 2 valid combinations for stability analysis
            # Basic results (first and last for backward compatibility)
            basic_result = {
                'participant_id': participant_id,
                'DAT_first7': all_dat_scores.get('DAT_first7'),
                'DAT_last7': all_dat_scores.get('DAT_last7'),
                'valid_words_count': valid_count
            }
            basic_results.append(basic_result)

            # All combinations results
            combo_result = {'participant_id': participant_id}
            combo_result.update(all_dat_scores)
            combo_result['valid_words_count'] = valid_count
            all_combinations_results.append(combo_result)

            # Calculate stability metrics
            stability_metrics = calculate_stability_metrics(valid_dat_scores)
            stability_result = {'participant_id': participant_id}
            stability_result.update(stability_metrics)
            stability_result['valid_words_count'] = valid_count
            stability_results.append(stability_result)

            print(f"Processed {participant_id}: {len(valid_dat_scores)} valid combinations, Mean = {stability_metrics.get('mean', 0):.2f}, SD = {stability_metrics.get('std_dev', 0):.3f}")
        else:
            # Not enough valid words
            basic_result = {
                'participant_id': participant_id,
                'DAT_first7': None,
                'DAT_last7': None,
                'valid_words_count': valid_count
            }
            basic_results.append(basic_result)
            print(f"Processed {participant_id}: Insufficient valid words ({valid_count} < 7)")

    # Create results dataframes
    basic_df = pd.DataFrame(basic_results)
    stability_df = pd.DataFrame(stability_results)
    all_combinations_df = pd.DataFrame(all_combinations_results)
    invalid_words_df = pd.DataFrame(invalid_words_results)

    # Save basic results (backward compatibility)
    output_file = "output/dat_scores_results.xlsx"
    basic_df.to_excel(output_file, index=False)

    # Save comprehensive stability analysis
    stability_output = "output/dat_stability_analysis.xlsx"
    with pd.ExcelWriter(stability_output) as writer:
        stability_df.to_excel(writer, sheet_name='Stability_Metrics', index=False)
        all_combinations_df.to_excel(writer, sheet_name='All_Combinations', index=False)

    # Save invalid words analysis
    invalid_words_output = "output/dat_invalid_words.xlsx"
    if len(invalid_words_df) > 0:
        with pd.ExcelWriter(invalid_words_output) as writer:
            invalid_words_df.to_excel(writer, sheet_name='Invalid_Words', index=False)

            # Create summary of invalid words by participant
            invalid_summary = invalid_words_df.groupby('participant_id').agg({
                'invalid_word': 'count',
                'reason': lambda x: x.value_counts().to_dict()
            }).rename(columns={'invalid_word': 'total_invalid_words'})
            invalid_summary.to_excel(writer, sheet_name='Invalid_Summary')

            # Create summary of most common invalid words
            word_frequency = invalid_words_df[invalid_words_df['reason'] == 'Not in vocabulary']['invalid_word'].value_counts().head(20)
            if len(word_frequency) > 0:
                freq_df = pd.DataFrame({
                    'word': word_frequency.index,
                    'frequency': word_frequency.values
                })
                freq_df.to_excel(writer, sheet_name='Most_Common_Invalid', index=False)
    else:
        print("No invalid words found.")

    # Print summary statistics
    print("\nSummary:")
    print(f"Total participants: {len(basic_df)}")
    print(f"Participants with valid DAT scores: {len(basic_df[basic_df['DAT_first7'].notna()])}")

    if len(invalid_words_df) > 0:
        print("\nInvalid Words Summary:")
        print(f"Total invalid word entries: {len(invalid_words_df)}")

    if len(basic_df[basic_df['DAT_first7'].notna()]) > 0:
        print("\nDAT First 7 Statistics:")
        print(f"Average: {basic_df['DAT_first7'].mean():.2f}")
        print(f"Min: {basic_df['DAT_first7'].min():.2f}")
        print(f"Max: {basic_df['DAT_first7'].max():.2f}")

        print("\nDAT Last 7 Statistics:")
        print(f"Average: {basic_df['DAT_last7'].mean():.2f}")
        print(f"Min: {basic_df['DAT_last7'].min():.2f}")
        print(f"Max: {basic_df['DAT_last7'].max():.2f}")

    return basic_df, stability_df, all_combinations_df, invalid_words_df

# Run the processing
if __name__ == "__main__":
    basic_results, stability_results, all_combinations_results, invalid_words_results = process_dat_responses()
