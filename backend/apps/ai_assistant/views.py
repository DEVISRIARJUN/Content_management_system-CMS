import re
import math
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status


def count_syllables(word):
    word = word.lower().strip(".:;?!")
    if not word:
        return 1
    # Count vowel groups
    count = len(re.findall(r'[aeiouy]+', word))
    if word.endswith("e") and not word.endswith("le") and count > 1:
        count -= 1
    return max(1, count)


class ReadabilityAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = request.data.get('text', '')
        # Clean HTML tags
        clean_text = re.sub(r'<[^>]+>', ' ', text).strip()
        
        words = re.findall(r'\b[A-Za-z0-9\'-]+\b', clean_text)
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

        word_count = len(words)
        sentence_count = max(1, len(sentences))
        
        if word_count == 0:
            return Response({
                "word_count": 0,
                "sentence_count": 0,
                "reading_time_mins": 0,
                "flesch_score": 100,
                "grade_level": "None",
                "notes": "Add content to see readability metrics."
            })

        total_syllables = sum(count_syllables(w) for w in words)
        words_per_sentence = word_count / sentence_count
        syllables_per_word = total_syllables / word_count

        # Flesch Reading Ease Formula
        score = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        score = max(0, min(100, round(score, 1)))

        if score >= 80:
            grade = "Very Easy (Grade 5-6)"
            note = "Accessible to a wide general audience."
        elif score >= 60:
            grade = "Standard (Grade 7-9)"
            note = "Ideal for blog posts and technical guides."
        elif score >= 40:
            grade = "Fairly Difficult (High School / College)"
            note = "Best for academic or in-depth technical readers."
        else:
            grade = "Very Difficult (Academic / Specialized)"
            note = "Consider shortening long sentences and simplifying vocabulary."

        reading_time_mins = max(1, math.ceil(word_count / 200))

        return Response({
            "word_count": word_count,
            "sentence_count": sentence_count,
            "reading_time_mins": reading_time_mins,
            "flesch_score": score,
            "grade_level": grade,
            "notes": note,
            "avg_words_per_sentence": round(words_per_sentence, 1)
        })


class SeoSuggestionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        title = request.data.get('title', '').strip()
        content = request.data.get('content', '')
        excerpt = request.data.get('excerpt', '').strip()
        keywords = request.data.get('keywords', '').strip()

        clean_content = re.sub(r'<[^>]+>', ' ', content)
        words = re.findall(r'\b[A-Za-z0-9\'-]+\b', clean_content)
        word_count = len(words)

        checklist = []
        score = 100

        # Title check
        title_len = len(title)
        if 40 <= title_len <= 65:
            checklist.append({"item": "Title length", "status": "pass", "msg": f"Optimal length ({title_len} chars)."})
        elif title_len < 40:
            checklist.append({"item": "Title length", "status": "warn", "msg": f"Short title ({title_len} chars). Aim for 45-60."})
            score -= 10
        else:
            checklist.append({"item": "Title length", "status": "warn", "msg": f"Title may get truncated on Google ({title_len} chars)."})
            score -= 10

        # Excerpt / Meta description check
        excerpt_len = len(excerpt)
        if 120 <= excerpt_len <= 160:
            checklist.append({"item": "Meta description", "status": "pass", "msg": f"Great snippet length ({excerpt_len} chars)."})
        elif excerpt_len == 0:
            checklist.append({"item": "Meta description", "status": "fail", "msg": "Missing meta description / excerpt."})
            score -= 20
        else:
            checklist.append({"item": "Meta description", "status": "warn", "msg": f"Currently {excerpt_len} chars. Target 130-155."})
            score -= 10

        # Content length check
        if word_count >= 300:
            checklist.append({"item": "Content depth", "status": "pass", "msg": f"Good depth ({word_count} words)."})
        else:
            checklist.append({"item": "Content depth", "status": "warn", "msg": f"Under 300 words ({word_count} words). Add more details."})
            score -= 15

        # Suggested SEO Title and Description if missing or poor
        suggested_title = title if title else "Complete Guide to Modern Web Development"
        suggested_description = excerpt if excerpt else (
            f"Discover everything you need to know about {title or 'this topic'} with clear steps, architecture insights, and practical examples."
        )

        return Response({
            "seo_score": max(20, score),
            "checklist": checklist,
            "suggested_title": suggested_title,
            "suggested_description": suggested_description[:155],
            "estimated_search_preview": {
                "title": suggested_title,
                "url": f"https://example.com/posts/{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') or 'article'}",
                "snippet": suggested_description[:150] + "..."
            }
        })


class SmartTagSuggesterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        title = request.data.get('title', '')
        content = request.data.get('content', '')
        combined = f"{title} {content}".lower()

        # Popular topic dictionary for matching
        topics_pool = [
            'Python', 'Django', 'React', 'JavaScript', 'TypeScript', 'API',
            'Full Stack', 'Backend', 'Frontend', 'Database', 'MySQL', 'PostgreSQL',
            'Redis', 'AWS', 'Docker', 'AI', 'Machine Learning', 'Tutorial',
            'Performance', 'Security', 'Architecture', 'CSS', 'Tailwind',
            'Cloud', 'DevOps', 'Next.js', 'Guide', 'Open Source'
        ]

        suggested = []
        for topic in topics_pool:
            if re.search(r'\b' + re.escape(topic.lower()) + r'\b', combined):
                suggested.append(topic)

        # Fallback to general tags if few matches
        if len(suggested) < 3:
            suggested.extend(['Engineering', 'Web Development', 'Technology'])

        return Response({
            "suggested_tags": list(dict.fromkeys(suggested))[:6]
        })


class SummarizerView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        content = request.data.get('content', '')
        clean = re.sub(r'<[^>]+>', ' ', content).strip()
        sentences = [s.strip() for s in re.split(r'[.!?]+', clean) if len(s.strip()) > 20]

        if not sentences:
            return Response({"summary": "Add more content to generate a summary."})

        # Pick key introductory and concluding sentences
        summary = sentences[0]
        if len(sentences) > 1:
            summary += ". " + sentences[min(len(sentences) - 1, 2)] + "."
        else:
            summary += "."

        return Response({
            "summary": summary
        })
