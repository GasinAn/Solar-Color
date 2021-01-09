from sklearn.manifold import TSNE

def t_SNE(data, perplexity):
    """
    data: [spec_0, spec_1,...], has shape (N_data, N_lambda)
    perplexity: perplexity
    Return 2D points after t-SNE
    """
    return TSNE(n_components=2, perplexity=perplexity).fit_transform(data)
