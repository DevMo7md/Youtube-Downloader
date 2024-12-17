from django.shortcuts import render
from django.contrib import messages
import yt_dlp

def home(request):
    context = {}  # إنشاء السياق بشكل مبدئي

    if 'link' in request.GET:  # التحقق من وجود الرابط
        link = request.GET['link']

        if link:  # التحقق أن الرابط ليس فارغًا
            try:
                # إعداد خيارات yt-dlp
                ydl_opts = {
                    'quiet': True,  # إيقاف الرسائل الغير مهمة
                    'no_warnings': True,  # عدم إظهار التحذيرات
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # استخراج معلومات الفيديو
                    info_dict = ydl.extract_info(link, download=False)
                    
                    # إضافة البيانات للسياق
                    context['title'] = info_dict.get('title', 'Unknown')
                    context['thumb'] = info_dict.get('thumbnail', '')
                    context['author'] = info_dict.get('uploader', 'Unknown')
                    context['likes'] = info_dict.get('like_count', 0)
                    context['dislikes'] = info_dict.get('dislike_count', 0)
                    context['link'] = link

                    # تصنيف الجودات إلى فيديو وصوت
                    video_streams = []
                    audio_streams = []
                    
                    for stream in info_dict.get('formats', []):
                        if stream.get('url'):  # تأكد من وجود رابط التنزيل
                            vcodec = stream.get('vcodec', '') or 'none'
                            acodec = stream.get('acodec', '') or 'none'
                            
                            # جودات الفيديو والصوت معًا
                            if vcodec != 'none' and acodec != 'none':
                                video_streams.append({
                                    'resolution': f"{stream.get('format_note', 'N/A')} - {stream.get('ext')}",
                                    'url': stream.get('url'),
                                })
                            # جودات الصوت فقط
                            elif acodec != 'none' and vcodec == 'none':
                                audio_streams.append({
                                    'resolution': f"Audio - {stream.get('ext')} - {stream.get('abr', 'N/A')} kbps",
                                    'url': stream.get('url'),
                                })

                    
                    context['video_streams'] = video_streams
                    context['audio_streams'] = audio_streams

            except Exception as e:  # التعامل مع الأخطاء المحتملة
                messages.error(request, f"عذرًا، حدث خطأ أثناء معالجة الرابط: {e}")
        else:
            messages.error(request, "عفواً الرابط غير موجود أو فارغ")
    else:
        messages.info(request, "الرجاء إدخال رابط لتحميل الفيديو")

    # تمرير السياق إلى الصفحة
    return render(request, 'home.html', context)
