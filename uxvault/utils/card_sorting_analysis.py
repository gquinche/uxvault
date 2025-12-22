"""
Card sorting analysis utilities for processing response data and generating analysis structures.

This module provides functions to process sorted card data from responses and build
dataframes suitable for dendrograms and co-occurrence matrix analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple


def extract_sorted_cards_from_responses(responses: List[Dict[str, Any]]) -> Tuple[List[List[str]], List[str]]:
    """
    Extracts all card groupings from multiple responses into a single flat list.

    Handles the data structure where 'sorted_cards' is a dictionary of
    { 'category_name': ['card1', 'card2', ...] }.

    Args:
        responses: List of response dictionaries from the dashboard.

    Returns:
        Tuple of (all_groups, processed_response_ids) where:
        - all_groups: A flat list of all card groups from all responses.
        - processed_response_ids: A list of unique response IDs that contained card data.
    """
    all_groups = []
    processed_response_ids = []

    for response in responses:
        response_id = response.get('id')
        response_data = response.get('response_data', {})

        sorted_cards = response_data.get('sorted_cards', {}) if isinstance(response_data, dict) else {}

        if sorted_cards:
            groups_in_this_response = False
            # `sorted_cards` is a dict of category_name: [card1, card2, ...]
            # We flatten this into a list of lists of cards (one list per category)
            for cards_in_category in sorted_cards.values():
                if cards_in_category and isinstance(cards_in_category, list):
                    all_groups.append(cards_in_category)
                    groups_in_this_response = True

            if groups_in_this_response and response_id:
                processed_response_ids.append(response_id)

    # Return all groups flattened and the unique IDs of responses that were processed
    return all_groups, list(set(processed_response_ids))

def extract_category_assignments_from_responses(responses: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, List[str]]], List[str]]:
    """
    Extracts category assignments from responses, preserving the mapping of cards to categories.

    This function is specifically designed for closed card sorting analysis where we need to track
    which categories each card was assigned to across different responses.

    Args:
        responses: List of response dictionaries from the dashboard.

    Returns:
        Tuple of (category_assignments, processed_response_ids) where:
        - category_assignments: Dictionary mapping response_id to {category_name: [card1, card2, ...]}
        - processed_response_ids: List of unique response IDs that contained card data
    """
    category_assignments = {}
    processed_response_ids = []

    for response in responses:
        response_id = response.get('id')
        response_data = response.get('response_data', {})

        sorted_cards = response_data.get('sorted_cards', {}) if isinstance(response_data, dict) else {}

        if sorted_cards and response_id:
            # Store the full category-to-cards mapping for this response
            category_assignments[response_id] = sorted_cards
            processed_response_ids.append(response_id)

    return category_assignments, list(set(processed_response_ids))


def build_cooccurrence_matrix(all_groups: List[List[str]]) -> Tuple[pd.DataFrame, List[str]]:
    """
    Build a co-occurrence matrix from a flat list of card groupings.
    
    Cards that appear together in the same group are counted.
    
    Args:
        all_groups: A list of card groups. Each group is a list of card IDs (strings).
        
    Returns:
        Tuple of (cooccurrence_df, unique_cards) where:
        - cooccurrence_df: DataFrame with co-occurrence counts (cards x cards).
        - unique_cards: Sorted list of all unique cards found.
    """
    # Collect all unique cards from all groups
    unique_cards = set()
    for group in all_groups:
        for card in group:
            unique_cards.add(str(card))
    
    unique_cards = sorted(list(unique_cards))
    
    # Initialize an empty co-occurrence matrix
    cooccurrence = pd.DataFrame(0, index=unique_cards, columns=unique_cards)
    
    # Populate the matrix with co-occurrence counts
    for group in all_groups:
        # Increment count for each pair of cards within the group
        for i, card1 in enumerate(group):
            for card2 in group[i:]: # Start from current position to avoid double counting
                if card1 == card2:
                    continue  # Do not count a card co-occurring with itself
                
                # Symmetrically increment the count for the pair
                cooccurrence.loc[card1, card2] += 1
                cooccurrence.loc[card2, card1] += 1
    
    return cooccurrence, unique_cards


def build_similarity_matrix(cooccurrence: pd.DataFrame) -> pd.DataFrame:
    """
    Build a normalized similarity matrix from co-occurrence counts.
    
    Uses Jaccard similarity based on co-occurrence patterns.
    
    Args:
        cooccurrence: Co-occurrence matrix (cards x cards)
        
    Returns:
        Similarity matrix (cards x cards) with values between 0 and 1
    """
    # Create a copy to avoid modifying the original
    similarity = cooccurrence.copy().astype(float)
    
    # Calculate Jaccard similarity: intersection / union
    cards = cooccurrence.index.tolist()
    n = len(cards)
    
    for i in range(n):
        for j in range(i, n):
            card1, card2 = cards[i], cards[j]
            
            intersection = cooccurrence.loc[card1, card2]
            union = (cooccurrence.loc[card1].sum() + cooccurrence.loc[card2].sum() - 
                    cooccurrence.loc[card1, card2])
            
            if union > 0:
                jaccard = intersection / union
            else:
                jaccard = 0.0
            
            similarity.loc[card1, card2] = jaccard
            similarity.loc[card2, card1] = jaccard
    
    return similarity


def build_distance_matrix(similarity: pd.DataFrame) -> pd.DataFrame:
    """
    Build a distance matrix from similarity matrix.
    
    Distance = 1 - Similarity
    
    Args:
        similarity: Similarity matrix (cards x cards)
        
    Returns:
        Distance matrix suitable for hierarchical clustering
    """
    return 1 - similarity


def build_analysis_dataframe(
    responses: List[Dict[str, Any]],
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Build a comprehensive analysis dataframe and matrices from selected responses.
    
    Args:
        responses: List of response dictionaries from dashboard
        include_metadata: Whether to include response metadata in output
        
    Returns:
        Dictionary containing:
        - 'groupings': Raw card groupings per response
        - 'response_ids': Response IDs corresponding to groupings
        - 'cooccurrence': Co-occurrence matrix
        - 'similarity': Similarity matrix
        - 'distance': Distance matrix for clustering
        - 'unique_cards': List of unique cards
        - 'metadata': Response metadata if include_metadata=True
    """
    groupings, response_ids = extract_sorted_cards_from_responses(responses)
    
    if not groupings:
        return {
            'groupings': [],
            'response_ids': [],
            'cooccurrence': None,
            'similarity': None,
            'distance': None,
            'unique_cards': [],
            'metadata': []
        }
    
    cooccurrence, unique_cards = build_cooccurrence_matrix(groupings)
    similarity = build_similarity_matrix(cooccurrence)
    distance = build_distance_matrix(similarity)
    
    metadata = []
    if include_metadata:
        # Filter responses to only include those that were processed
        processed_responses = [r for r in responses if r.get('id') in response_ids]
        for response in processed_responses:
            metadata.append({
                'response_id': response.get('id'),
                'survey_id': response.get('survey_id'),
                'completed_at': response.get('response_data', {}).get('completed_at'),
            })
    
    return {
        'groupings': groupings,
        'response_ids': response_ids,
        'cooccurrence': cooccurrence,
        'similarity': similarity,
        'distance': distance,
        'unique_cards': unique_cards,
        'metadata': metadata
    }


def flatten_groupings_to_pairs(all_groups: List[List[str]]) -> pd.DataFrame:
    """
    Convert a flat list of groupings to a dataframe of card pairs.

    Each row represents a pair of cards that were grouped together.

    Args:
        all_groups: A flat list of card groups from all responses.

    Returns:
        DataFrame with columns: card1, card2, together_count.
    """
    pairs = []

    for group in all_groups:
        # Create pairs from the cards in the group
        for i, card1 in enumerate(group):
            for card2 in group[i+1:]: # Start from i+1 to avoid self-pairs and duplicates
                pairs.append({
                    'card1': min(str(card1), str(card2)),  # Normalize pair order
                    'card2': max(str(card1), str(card2)),
                })

    if not pairs:
        return pd.DataFrame(columns=['card1', 'card2', 'together_count'])

    pairs_df = pd.DataFrame(pairs)

    # Count how many times each pair appeared together
    if not pairs_df.empty:
        pairs_df = pairs_df.groupby(['card1', 'card2']).size().reset_index(name='together_count')

    return pairs_df

def build_category_assignment_matrix(category_assignments: Dict[str, Dict[str, List[str]]]) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Build a category assignment matrix showing how many times each card was assigned to each category.

    Args:
        category_assignments: Dictionary mapping response_id to {category_name: [card1, card2, ...]}

    Returns:
        Tuple of (category_matrix, unique_cards, unique_categories) where:
        - category_matrix: DataFrame with cards as rows, categories as columns, and counts as values
        - unique_cards: Sorted list of all unique cards
        - unique_categories: Sorted list of all unique categories
    """
    # Collect all unique cards and categories
    unique_cards = set()
    unique_categories = set()

    for response_data in category_assignments.values():
        for category, cards in response_data.items():
            unique_categories.add(category)
            for card in cards:
                unique_cards.add(str(card))

    unique_cards = sorted(list(unique_cards))
    unique_categories = sorted(list(unique_categories))

    # Initialize matrix with zeros
    category_matrix = pd.DataFrame(0, index=unique_cards, columns=unique_categories)

    # Populate the matrix
    for response_data in category_assignments.values():
        for category, cards in response_data.items():
            for card in cards:
                card_str = str(card)
                if card_str in category_matrix.index and category in category_matrix.columns:
                    category_matrix.loc[card_str, category] += 1

    return category_matrix, unique_cards, unique_categories

def build_category_consistency_matrix(category_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Build a category consistency matrix showing the proportion of times each card was assigned to each category.

    Args:
        category_matrix: Category assignment matrix from build_category_assignment_matrix

    Returns:
        DataFrame with normalized proportions (values between 0 and 1)
    """
    # Calculate row sums (total assignments per card)
    row_sums = category_matrix.sum(axis=1)

    # Avoid division by zero - set zero rows to 1 to prevent NaN
    row_sums[row_sums == 0] = 1

    # Normalize by dividing each row by its sum
    consistency_matrix = category_matrix.div(row_sums, axis=0)

    return consistency_matrix

def build_category_popularity_analysis(category_assignments: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
    """
    Analyze category popularity and usage patterns.

    Args:
        category_assignments: Dictionary mapping response_id to {category_name: [card1, card2, ...]}

    Returns:
        Dictionary containing:
        - 'category_counts': Count of cards per category across all responses
        - 'category_usage': Count of responses that used each category
        - 'average_cards_per_category': Average number of cards per category
        - 'category_size_distribution': Distribution of category sizes
    """
    category_counts = {}
    category_usage = {}

    # Count cards per category and track which responses used each category
    for response_data in category_assignments.values():
        for category, cards in response_data.items():
            # Count cards in this category
            card_count = len(cards)
            category_counts[category] = category_counts.get(category, 0) + card_count

            # Track category usage
            category_usage[category] = category_usage.get(category, 0) + 1

    # Calculate additional metrics
    total_responses = len(category_assignments)
    total_categories = len(category_counts)

    average_cards_per_category = {
        category: count / category_usage.get(category, 1)
        for category, count in category_counts.items()
    }

    # Create distribution of category sizes
    category_size_distribution = {}
    for response_data in category_assignments.values():
        for category, cards in response_data.items():
            size = len(cards)
            category_size_distribution[category] = category_size_distribution.get(category, [])
            category_size_distribution[category].append(size)

    return {
        'category_counts': category_counts,
        'category_usage': category_usage,
        'average_cards_per_category': average_cards_per_category,
        'category_size_distribution': category_size_distribution,
        'total_responses': total_responses,
        'total_categories': total_categories
    }

def build_comprehensive_category_analysis(
    responses: List[Dict[str, Any]],
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Build a comprehensive category-level analysis for closed card sortings.

    Args:
        responses: List of response dictionaries from dashboard
        include_metadata: Whether to include response metadata in output

    Returns:
        Dictionary containing:
        - 'category_assignments': Raw category assignments per response
        - 'response_ids': Response IDs that were processed
        - 'category_matrix': Category assignment matrix (cards x categories)
        - 'consistency_matrix': Category consistency matrix (normalized)
        - 'category_popularity': Category popularity analysis
        - 'unique_cards': List of unique cards
        - 'unique_categories': List of unique categories
        - 'metadata': Response metadata if include_metadata=True
    """
    category_assignments, response_ids = extract_category_assignments_from_responses(responses)

    if not category_assignments:
        return {
            'category_assignments': {},
            'response_ids': [],
            'category_matrix': None,
            'consistency_matrix': None,
            'category_popularity': None,
            'unique_cards': [],
            'unique_categories': [],
            'metadata': []
        }

    category_matrix, unique_cards, unique_categories = build_category_assignment_matrix(category_assignments)
    consistency_matrix = build_category_consistency_matrix(category_matrix)
    category_popularity = build_category_popularity_analysis(category_assignments)

    metadata = []
    if include_metadata:
        # Filter responses to only include those that were processed
        processed_responses = [r for r in responses if r.get('id') in response_ids]
        for response in processed_responses:
            metadata.append({
                'response_id': response.get('id'),
                'survey_id': response.get('survey_id'),
                'completed_at': response.get('response_data', {}).get('completed_at'),
            })

    return {
        'category_assignments': category_assignments,
        'response_ids': response_ids,
        'category_matrix': category_matrix,
        'consistency_matrix': consistency_matrix,
        'category_popularity': category_popularity,
        'unique_cards': unique_cards,
        'unique_categories': unique_categories,
        'metadata': metadata
    }
