from django.shortcuts import render, redirect
from .forms import SearchForm
from .models import Website, NavbarLink
from .scrapper import scrape_navbar_links
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import threading
from .scrapper import stop_scraping_immediately

# Global variable to track scraping state
scraping_thread = None
stop_event = threading.Event()

def home(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            website_url, nav_links = scrape_navbar_links(query)

            website = Website.objects.create(query=query, url=website_url)
            for text, href in nav_links:
                NavbarLink.objects.create(website=website, text=text, href=href)

            return redirect('results', website_id=website.id)
    else:
        form = SearchForm()
    return render(request, 'home.html', {'form': form})

def results(request, website_id):
    website = Website.objects.get(id=website_id)
    return render(request, 'results.html', {'website': website})


@require_POST
def stop_extraction(request):
    print('destroyer hit')
    global stop_event
    stop_event.set()
    stop_scraping_immediately()
    return JsonResponse({'status': 'stopped', 'message': 'Extraction process stopped successfully'})

