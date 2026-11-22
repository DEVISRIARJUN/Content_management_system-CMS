import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.posts.models import Category, Tag, Post, PostRevision
from apps.analytics.models import PageView
from apps.media_manager.models import MediaAsset
from django.utils import timezone
from datetime import timedelta
import random


def seed():
    print("[*] Seeding database with realistic production CMS content...")

    # 1. Superuser / Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@novacms.io',
            'first_name': 'Alexander',
            'last_name': 'Vance',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("  [+] Created Superuser: admin / admin123")
    
    if hasattr(admin_user, 'profile'):
        admin_user.profile.role = 'admin'
        admin_user.profile.bio = 'Lead Platform Architect & Editorial Director.'
        admin_user.profile.avatar_url = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=250&q=80'
        admin_user.profile.twitter_handle = 'alexvance_dev'
        admin_user.profile.save()

    # 2. Staff Author
    author_user, created = User.objects.get_or_create(
        username='sarah_dev',
        defaults={
            'email': 'sarah@novacms.io',
            'first_name': 'Sarah',
            'last_name': 'Chen',
            'is_staff': False
        }
    )
    if created:
        author_user.set_password('author123')
        author_user.save()
        print("  [+] Created Author: sarah_dev / author123")
    
    if hasattr(author_user, 'profile'):
        author_user.profile.role = 'editor'
        author_user.profile.bio = 'Senior Full Stack Engineer & Cloud Systems Specialist.'
        author_user.profile.avatar_url = 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=250&q=80'
        author_user.profile.github_handle = 'sarahchen'
        author_user.profile.save()

    # 3. Categories
    categories_data = [
        {"name": "Engineering & Architecture", "slug": "engineering", "color_hex": "#2563EB", "icon": "Cpu", "desc": "Deep dives into system design, databases, and scalable backend architecture."},
        {"name": "AI & Machine Learning", "slug": "ai-ml", "color_hex": "#8B5CF6", "icon": "Brain", "desc": "Practical implementations of AI workflows, NLP, and model serving."},
        {"name": "Frontend & UI Design", "slug": "frontend", "color_hex": "#EC4899", "icon": "Layout", "desc": "Modern user interfaces, component systems, and responsive design patterns."},
        {"name": "Cloud & DevOps", "slug": "cloud-devops", "color_hex": "#10B981", "icon": "Cloud", "desc": "Containerization, CI/CD pipelines, AWS infrastructure, and site reliability."},
        {"name": "Product & Strategy", "slug": "product-strategy", "color_hex": "#F59E0B", "icon": "TrendingUp", "desc": "Product metrics, feature prioritization, and engineering management."},
    ]

    category_objs = {}
    for cat in categories_data:
        obj, _ = Category.objects.get_or_create(
            slug=cat['slug'],
            defaults={
                'name': cat['name'],
                'color_hex': cat['color_hex'],
                'icon': cat['icon'],
                'description': cat['desc'],
                'is_featured': True
            }
        )
        category_objs[cat['slug']] = obj
    print(f"  [+] Configured {len(category_objs)} categories.")

    # 4. Tags
    tag_names = ["Python", "Django", "React", "MySQL", "AWS S3", "Redis", "TypeScript", "Tailwind CSS", "Architecture", "Security"]
    tag_objs = {}
    for name in tag_names:
        t, _ = Tag.objects.get_or_create(name=name)
        tag_objs[name] = t

    # 5. Realistic Sample Posts with Block-Based Data
    posts_data = [
        {
            "title": "Designing a High-Throughput Headless CMS with Python and MySQL",
            "slug": "designing-high-throughput-headless-cms",
            "author": admin_user,
            "status": "published",
            "excerpt": "How we decoupled backend content storage from presentation layers using Django REST Framework, block-based JSON serialization, and Redis caching.",
            "featured_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
            "categories": [category_objs["engineering"], category_objs["cloud-devops"]],
            "tags": [tag_objs["Python"], tag_objs["Django"], tag_objs["MySQL"], tag_objs["Architecture"]],
            "seo_title": "Designing a High-Throughput Headless CMS with Python & MySQL",
            "seo_description": "Explore architecture patterns for building a modern headless CMS using Django, block schemas, and MySQL caching.",
            "seo_keywords": "headless cms, django, mysql, python full stack, redis caching",
            "blocks": [
                {
                    "id": "b1",
                    "type": "heading",
                    "level": 2,
                    "text": "The Evolution from Monolithic to Decoupled CMS"
                },
                {
                    "id": "b2",
                    "type": "paragraph",
                    "text": "Traditional CMS platforms bundled presentation templates, plugin execution, and database writes into a single synchronous thread. In high-traffic scenarios, this created severe CPU bottlenecks. By decoupling our API from client frontends, we enable lightning-fast static generation, mobile integration, and independent scaling."
                },
                {
                    "id": "b3",
                    "type": "alert",
                    "variant": "info",
                    "text": "Pro-tip: Always store block content as structured JSON instead of flat HTML. This gives you total flexibility to render components natively in React, Flutter, or iOS."
                },
                {
                    "id": "b4",
                    "type": "heading",
                    "level": 3,
                    "text": "Database Strategy: MySQL 8 with JSON Columns"
                },
                {
                    "id": "b5",
                    "type": "code",
                    "language": "python",
                    "code": "# Example of dynamic revision snapshotting\ndef save_revision(post, user):\n    return PostRevision.objects.create(\n        post=post,\n        blocks_data_snapshot=post.blocks_data,\n        author=user,\n        version_number=post.revisions.count() + 1\n    )"
                },
                {
                    "id": "b6",
                    "type": "paragraph",
                    "text": "By leveraging MySQL 8 JSON validation combined with Django ORM, we preserve relational integrity for users, permissions, and media while maintaining arbitrary block flexibility for article layouts."
                }
            ],
            "html": "<h2>The Evolution from Monolithic to Decoupled CMS</h2><p>Traditional CMS platforms bundled presentation templates, plugin execution, and database writes into a single synchronous thread. In high-traffic scenarios, this created severe CPU bottlenecks. By decoupling our API from client frontends, we enable lightning-fast static generation, mobile integration, and independent scaling.</p><blockquote>Pro-tip: Always store block content as structured JSON instead of flat HTML. This gives you total flexibility to render components natively in React, Flutter, or iOS.</blockquote><h3>Database Strategy: MySQL 8 with JSON Columns</h3><pre><code># Example of dynamic revision snapshotting\ndef save_revision(post, user):\n    return PostRevision.objects.create(\n        post=post,\n        blocks_data_snapshot=post.blocks_data,\n        author=user,\n        version_number=post.revisions.count() + 1\n    )</code></pre><p>By leveraging MySQL 8 JSON validation combined with Django ORM, we preserve relational integrity for users, permissions, and media while maintaining arbitrary block flexibility for article layouts.</p>",
            "views": 1420
        },
        {
            "title": "Direct S3 Presigned Uploads: Eliminating Server Bottlenecks",
            "slug": "direct-s3-presigned-uploads-guide",
            "author": author_user,
            "status": "published",
            "excerpt": "Why proxying large file uploads through your application server hurts latency, and how to safely generate short-lived AWS S3 presigned URLs.",
            "featured_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80",
            "categories": [category_objs["cloud-devops"], category_objs["engineering"]],
            "tags": [tag_objs["AWS S3"], tag_objs["Security"], tag_objs["Django"]],
            "seo_title": "Direct S3 Presigned Uploads: Complete Implementation Guide",
            "seo_description": "Learn how to bypass your Django backend for direct, secure file uploads into AWS S3 using presigned PUT tokens.",
            "seo_keywords": "aws s3, presigned urls, file upload, django media, cloud storage",
            "blocks": [
                {
                    "id": "b1",
                    "type": "heading",
                    "level": 2,
                    "text": "The Problem with Traditional Multi-Part Uploads"
                },
                {
                    "id": "b2",
                    "type": "paragraph",
                    "text": "When a client uploads a 50MB video file directly through your Django endpoint, that worker process is occupied for the entire transmission duration. During peak hours, a handful of concurrent uploads can exhaust all gunicorn/uWSGI workers."
                },
                {
                    "id": "b3",
                    "type": "quote",
                    "text": "Never let media transit through your core web application server when object storage can handle ingestion directly.",
                    "cite": "Cloud Architecture Principles"
                },
                {
                    "id": "b4",
                    "type": "paragraph",
                    "text": "The modern pattern is simple: the browser requests an authorization token from Django, uploads bytes directly to an S3 bucket via HTTP PUT, and notifies Django upon completion."
                }
            ],
            "html": "<h2>The Problem with Traditional Multi-Part Uploads</h2><p>When a client uploads a 50MB video file directly through your Django endpoint, that worker process is occupied for the entire transmission duration. During peak hours, a handful of concurrent uploads can exhaust all gunicorn/uWSGI workers.</p><blockquote>Never let media transit through your core web application server when object storage can handle ingestion directly.</blockquote><p>The modern pattern is simple: the browser requests an authorization token from Django, uploads bytes directly to an S3 bucket via HTTP PUT, and notifies Django upon completion.</p>",
            "views": 890
        },
        {
            "title": "Integrating Real-time AI Readability & SEO Scorer into Modern Editors",
            "slug": "integrating-real-time-ai-readability-seo",
            "author": author_user,
            "status": "published",
            "excerpt": "A deep dive into building real-time writing heuristics, Flesch Reading Ease calculators, and automated meta description generators into React and Django.",
            "featured_image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
            "categories": [category_objs["ai-ml"], category_objs["frontend"]],
            "tags": [tag_objs["Python"], tag_objs["React"], tag_objs["TypeScript"]],
            "seo_title": "Real-time AI Readability & SEO Scorer in Modern CMS Editors",
            "seo_description": "Build an intelligent writing assistant inside your CMS dashboard using NLP heuristics and Flesch Reading Ease algorithms.",
            "seo_keywords": "ai cms, readability score, flesch reading ease, automated seo, nlp assistant",
            "blocks": [
                {
                    "id": "b1",
                    "type": "heading",
                    "level": 2,
                    "text": "Empowering Content Authors with Instant Feedback"
                },
                {
                    "id": "b2",
                    "type": "paragraph",
                    "text": "Great content is not just about grammatical correctness—it is about clarity, pacing, and discoverability. By running lightweight NLP algorithms right as an author finishes a section, we provide instant visual guidance on sentence complexity and search readiness."
                }
            ],
            "html": "<h2>Empowering Content Authors with Instant Feedback</h2><p>Great content is not just about grammatical correctness—it is about clarity, pacing, and discoverability. By running lightweight NLP algorithms right as an author finishes a section, we provide instant visual guidance on sentence complexity and search readiness.</p>",
            "views": 2150
        },
        {
            "title": "Building a Drag-and-Drop Page Builder with React and Block Schemas",
            "slug": "drag-and-drop-page-builder-react",
            "author": admin_user,
            "status": "draft",
            "excerpt": "Drafting our upcoming architectural breakdown on block reordering, undo/redo states, and nested layouts.",
            "featured_image": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=1200&q=80",
            "categories": [category_objs["frontend"]],
            "tags": [tag_objs["React"], tag_objs["TypeScript"], tag_objs["Tailwind CSS"]],
            "seo_title": "Building a Drag-and-Drop Page Builder with React",
            "seo_description": "A comprehensive tutorial on creating block-based website builders.",
            "seo_keywords": "drag and drop, block editor, react, page builder",
            "blocks": [
                {
                    "id": "b1",
                    "type": "heading",
                    "level": 2,
                    "text": "Work in progress"
                },
                {
                    "id": "b2",
                    "type": "paragraph",
                    "text": "This draft is currently undergoing editorial review and will be published shortly."
                }
            ],
            "html": "<h2>Work in progress</h2><p>This draft is currently undergoing editorial review and will be published shortly.</p>",
            "views": 45
        }
    ]

    for p in posts_data:
        post, created = Post.objects.get_or_create(
            slug=p["slug"],
            defaults={
                "title": p["title"],
                "author": p["author"],
                "status": p["status"],
                "excerpt": p["excerpt"],
                "featured_image": p["featured_image"],
                "blocks_data": p["blocks"],
                "content_html": p["html"],
                "seo_title": p["seo_title"],
                "seo_description": p["seo_description"],
                "seo_keywords": p["seo_keywords"],
                "view_count": p["views"],
                "published_at": timezone.now() - timedelta(days=random.randint(1, 14)) if p["status"] == "published" else None
            }
        )
        post.categories.set(p["categories"])
        post.tags.set(p["tags"])
        if created:
            post.create_revision(user=p["author"], summary="Initial seeded version")
            print(f"  [+] Seeded post: {post.title}")

    # 6. Seed PageViews for the last 7 days for Analytics charts
    published_posts = Post.objects.filter(status='published')
    now = timezone.now()
    if PageView.objects.count() < 50:
        for day_offset in range(7):
            day_time = now - timedelta(days=day_offset)
            views_today = random.randint(35, 120)
            for _ in range(views_today):
                random_post = random.choice(published_posts)
                PageView.objects.create(
                    post=random_post,
                    path=f"/posts/{random_post.slug}/",
                    ip_address=f"192.168.1.{random.randint(10, 250)}",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0",
                    timestamp=day_time - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                )
        print("  [+] Seeded 7-day traffic analytics log.")

    print("[SUCCESS] Database seeding completed successfully!")


if __name__ == '__main__':
    seed()
