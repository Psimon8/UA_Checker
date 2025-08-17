"""
Définitions des bots et leurs User-Agents
"""

BOT_DEFINITIONS = {
    'openai': {
        'user_agent_pattern': r'gptbot|chatgpt-user|openai|oai-searchbot',
        'user_agents': {
            'GPTBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.1; +https://openai.com/gptbot',
            'ChatGPT-User': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot',
            'OAI-SearchBot': 'OAI-SearchBot/1.0; +https://openai.com/searchbot'
        }
    },
    'anthropic': {
        'user_agent_pattern': r'claude-bot|anthropic|claudebot',
        'user_agents': {
            'ClaudeBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)',
            'Claude-User': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +Claude-User@anthropic.com)'
        }
    },
    'perplexity': {
        'user_agent_pattern': r'perplexitybot|perplexity',
        'user_agents': {
            'PerplexityBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)',
            'Perplexity-User': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)'
        }
    },
    'googlebot': {
        'user_agent_pattern': r'googlebot',
        'user_agents': {
            'Googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Googlebot-Mobile': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/W.X.Y.Z Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }
    },
    'bingbot': {
        'user_agent_pattern': r'bingbot',
        'user_agents': {
            'BingBot': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'BingBot-Mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
        }
    },
    'yandexbot': {
        'user_agent_pattern': r'yandexbot',
        'user_agents': {
            'YandexBot': 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
            'YandexMobileBot': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B411 Safari/600.1.4 (compatible; YandexMobileBot/3.0; +http://yandex.com/bots)'
        }
    },
    'facebookbot': {
        'user_agent_pattern': r'facebookexternalhit',
        'user_agents': {
            'FacebookBot': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
            'FacebookBot-Mobile': 'Mozilla/5.0 (compatible; FacebookBot/1.0; +https://developers.facebook.com/docs/sharing/webmasters/crawler)'
        }
    },
    'twitterbot': {
        'user_agent_pattern': r'twitterbot',
        'user_agents': {
            'TwitterBot': 'Twitterbot/1.0',
            'TwitterBot-Compatible': 'Mozilla/5.0 (compatible; Twitterbot/1.0)'
        }
    },
    'linkedinbot': {
        'user_agent_pattern': r'linkedinbot',
        'user_agents': {
            'LinkedInBot': 'LinkedInBot/1.0 (compatible; Mozilla/5.0; +http://www.linkedin.com/)',
            'LinkedInBot-Compatible': 'Mozilla/5.0 (compatible; LinkedInBot/1.0; +http://www.linkedin.com/)'
        }
    },
    'cohere': {
        'user_agent_pattern': r'cohere-ai',
        'user_agents': {
            'CohereBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; Cohere-AI/1.0',
            'CohereBot-Simple': 'Cohere-AI/1.0'
        }
    }
}

BOT_MAPPING = {
    'google': 'googlebot', 
    'bing': 'bingbot', 
    'yandex': 'yandexbot',
    'openai': 'openai', 
    'anthropic': 'anthropic', 
    'perplexity': 'perplexity',
    'cohere': 'cohere', 
    'facebook': 'facebookbot', 
    'twitter': 'twitterbot',
    'linkedin': 'linkedinbot'
}
