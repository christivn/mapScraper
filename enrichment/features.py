import re
import math
import logging
import pandas as pd

logger = logging.getLogger(__name__)

_DOMAIN_RE = re.compile(
    r'^(www\.)?[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
    r'(\.[a-zA-Z]{2,})+$'
)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered feature columns to the scraped DataFrame.

    Input columns expected: phoneNumber, completePhoneNumber, domain, url, stars, reviews.
    Returns a new DataFrame with additional columns appended.
    """
    df = df.copy()

    phone = df.get('phoneNumber', pd.Series('', index=df.index)).fillna('')
    intl_phone = df.get('completePhoneNumber', pd.Series('', index=df.index)).fillna('')
    domain = df.get('domain', pd.Series('', index=df.index)).fillna('')
    url = df.get('url', pd.Series('', index=df.index)).fillna('')

    df['has_phone'] = (phone.str.strip() != '') | (intl_phone.str.strip() != '')
    df['has_website'] = (domain.str.strip() != '') | (url.str.strip() != '')
    df['domain_valid'] = domain.apply(_validate_domain)
    df['rating_score'] = _compute_rating_scores(df)
    df['review_density'] = _normalize_reviews(df.get('reviews', pd.Series(0, index=df.index)))

    logger.info("Feature engineering complete: %d rows, %d columns", len(df), len(df.columns))
    return df


def _validate_domain(domain: str) -> bool:
    if not domain or not isinstance(domain, str):
        return False
    return bool(_DOMAIN_RE.match(domain.strip()))


def _compute_rating_scores(df: pd.DataFrame) -> pd.Series:
    stars = pd.to_numeric(df.get('stars', pd.Series(0, index=df.index)), errors='coerce').fillna(0.0)
    reviews = pd.to_numeric(df.get('reviews', pd.Series(0, index=df.index)), errors='coerce').fillna(0.0)
    # stars (0–5) weighted by log of review volume to penalise suspiciously high
    # ratings with very few reviews
    return (stars * reviews.apply(lambda r: math.log1p(r))).round(4)


def _normalize_reviews(reviews_series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(reviews_series, errors='coerce').fillna(0.0)
    max_val = numeric.max()
    if max_val == 0:
        return pd.Series(0.0, index=reviews_series.index)
    return (numeric / max_val).round(4)
