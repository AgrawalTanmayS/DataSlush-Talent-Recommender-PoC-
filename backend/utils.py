import pandas as pd


def load_candidates(path='data/talent_profiles.csv'):
    df = pd.read_csv(path)
    df = df.fillna('')

    # Map dataset columns to the fields our recommender expects
    df['name'] = df['First Name'].astype(str) + ' ' + df['Last Name'].astype(str)
    df['bio'] = df['Profile Description']
    df['skills'] = df['Skills']
    df['software'] = df['Software']
    df['platforms'] = df['Platforms']
    df['niches'] = df['Content Verticals']
    df['worked_with'] = df['Past Creators']
    df['location'] = df['City'].astype(str) + ', ' + df['Country'].astype(str)

    # Normalize numeric values
    df['monthly_rate'] = pd.to_numeric(df['Monthly Rate'], errors='coerce').fillna(0.0)
    df['hourly_rate'] = pd.to_numeric(df['Hourly Rate'], errors='coerce').fillna(0.0)
    df['view_count'] = pd.to_numeric(df['# of Views by Creators'], errors='coerce').fillna(0.0)

    return df


def parse_job_postings():
    posts = []
    posts.append({
        'id': 'dslush_1',
        'title': 'Video Editor - Entertainment/Lifestyle & Vlogs',
        'description': 'Looking for a talented Video Editor with experience in Adobe Premiere Pro who can edit content in Entertainment/Lifestyle & Vlogs categories. Content: short-form and long-form. Top skills: Splice & Dice, Rough Cut & Sequencing, 2D Animation.',
        'required_skills': ['Splice & Dice', 'Rough Cut & Sequencing', '2D Animation', 'Adobe Premiere Pro'],
        'locations': ['Asia'],
        'budget_type': 'monthly',
        'budget': 2500
    })

    posts.append({
        'id': 'dslush_2',
        'title': 'Producer/Video Editor - New York / US Remote',
        'description': 'Hiring a Producer/Video Editor based in New York (1st priority) or remote from the US to help scale channel in Entertainment/Education/Food & Cooking. Wants deep TikTok experience. Skills: Storyboarding, Sound Designing, Rough Cut & Sequencing, Filming',
        'required_skills': ['Storyboarding', 'Sound Designing', 'Rough Cut & Sequencing', 'Filming', 'TikTok'],
        'locations': ['New York', 'United States'],
        'budget_type': 'hourly',
        'budget': [100, 150]
    })

    posts.append({
        'id': 'dslush_3',
        'title': 'Chief Operating Officer - Productivity',
        'description': 'COO to run large productivity channel. Background: Strategy & Consulting, Business operations or Development. Needs high energy and passion for educational content. No budget limit.',
        'required_skills': ['Strategy', 'Consulting', 'Business Operations', 'Leadership'],
        'locations': [],
        'budget_type': 'monthly',
        'budget': 99999999
    })

    return posts
