// Mobile Menu Toggle
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('.nav-menu-left');

if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        if (navMenu) {
            navMenu.classList.remove('active');
        }
    });
});

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const target = document.querySelector(targetId);
        if (target) {
            const offsetTop = target.offsetTop - 100;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Currency Conversion Constants
const USD_TO_BYN = 2.95;
const USD_TO_RUB = 78;
const DEFAULT_CURRENCY = 'BYN';

// Currency Symbols
const CURRENCY_SYMBOLS = {
    'USD': '$',
    'BYN': 'Br',
    'RUB': '₽'
};

// Convert USD price to selected currency
function convertPrice(usdPrice, currency) {
    switch(currency) {
        case 'BYN':
            return Math.round(usdPrice * USD_TO_BYN);
        case 'RUB':
            return Math.round(usdPrice * USD_TO_RUB);
        case 'USD':
            return usdPrice;
        default:
            return Math.round(usdPrice * USD_TO_BYN); // Default to BYN
    }
}

// Format price with currency symbol
function formatPrice(price, currency) {
    const symbol = CURRENCY_SYMBOLS[currency] || CURRENCY_SYMBOLS['BYN'];
    
    if (currency === 'USD') {
        return `${symbol}${price}`;
    } else {
        return `${price} ${symbol}`;
    }
}

// Subscription Plans Data (base prices in USD)
const plans = {
    light: {
        name: 'ЛАЙТ',
        priceUSD: 39,
        oldPriceUSD: 50,
        description: 'Самостоятельный тариф для начинающих'
    },
    start: {
        name: 'СТАРТ',
        priceUSD: 69,
        oldPriceUSD: 90,
        description: 'Для начинающих с поддержкой тренера'
    },
    optimal: {
        name: 'ОПТИМА',
        priceUSD: 99,
        oldPriceUSD: 150,
        description: 'Рекомендуемый тариф с регулярной поддержкой'
    },
    vip: {
        name: 'ПРЕМИУМ VIP',
        priceUSD: 199,
        oldPriceUSD: 350,
        description: 'Максимальное внимание и поддержка 24/7'
    }
};

// Modal Elements
const modal = document.getElementById('subscriptionModal');
const modalPlanName = document.getElementById('modalPlanName');
const modalPrice = document.getElementById('modalPrice');
const subscriptionForm = document.getElementById('subscriptionForm');
const modalClose = document.querySelector('.modal-close');

// Redirect to Bot on Service Button Click (Tariff Selection)
document.querySelectorAll('.btn-service').forEach(button => {
    button.addEventListener('click', () => {
        const planId = button.getAttribute('data-plan');
        const plan = plans[planId];
        
        if (plan) {
            // Get current currency
            const currentCurrency = localStorage.getItem('selectedCurrency') || DEFAULT_CURRENCY;
            
            // Redirect to Telegram bot with tariff and currency parameters
            const BOT_USERNAME = 'levelfitbot';
            const telegramUrl = `https://t.me/${BOT_USERNAME}?start=${planId}_${currentCurrency}`;
            window.open(telegramUrl, '_blank');
        }
    });
});

// Close Modal
if (modalClose) {
    modalClose.addEventListener('click', () => {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
}

// Close Modal when clicking outside
if (modal) {
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
}

// Handle Subscription Form Submission
if (subscriptionForm) {
    subscriptionForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(subscriptionForm);
        const planId = subscriptionForm.getAttribute('data-plan');
        const plan = plans[planId];
        
        if (plan) {
            const data = {
                plan: plan.name,
                price: plan.price,
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone')
            };
            
            // Here you would typically send this data to your backend
            console.log('Subscription Data:', data);
            
            // Show success message
            alert(`Спасибо, ${data.name}! Ваша заявка на подписку "${plan.name}" принята. Мы свяжемся с вами в ближайшее время.`);
            
            // Reset form and close modal
            subscriptionForm.reset();
            if (modal) {
                modal.style.display = 'none';
            }
            document.body.style.overflow = 'auto';
        }
    });
}

// Handle Goal Selection Form
const goalForm = document.querySelector('.goal-form');
if (goalForm) {
    goalForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const selectedGoal = goalForm.querySelector('input[name="goal"]:checked');
        if (selectedGoal) {
            const goalText = selectedGoal.closest('.radio-label').querySelector('.radio-text').textContent;
            
            // Scroll to subscriptions section
            const subscriptionsSection = document.getElementById('subscriptions');
            if (subscriptionsSection) {
                const offsetTop = subscriptionsSection.offsetTop - 100;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
            
            // You can store the selected goal for later use
            console.log('Selected goal:', goalText);
        } else {
            alert('Пожалуйста, выберите цель');
        }
    });
}

// Navbar Background on Scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
});

// Intersection Observer for Fade-in Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.service-card, .process-step, .goal-selection, .hero-content, .hero-image-container');
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(40px)';
        el.style.transition = `opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s, transform 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`;
        observer.observe(el);
    });
    
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length) {
        faqItems.forEach(item => {
            const questionButton = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');

            if (questionButton && answer) {
                questionButton.addEventListener('click', () => {
                    const isExpanded = questionButton.getAttribute('aria-expanded') === 'true';

                    faqItems.forEach(otherItem => {
                        if (otherItem === item) {
                            return;
                        }
                        const otherButton = otherItem.querySelector('.faq-question');
                        const otherAnswer = otherItem.querySelector('.faq-answer');
                        if (otherButton && otherAnswer) {
                            otherItem.classList.remove('active');
                            otherButton.setAttribute('aria-expanded', 'false');
                        }
                    });

                    if (!isExpanded) {
                        item.classList.add('active');
                        questionButton.setAttribute('aria-expanded', 'true');
                    } else {
                        item.classList.remove('active');
                        questionButton.setAttribute('aria-expanded', 'false');
                    }
                });
            }
        });
    }
    
    // Parallax effect for hero image
    const heroImage = document.querySelector('.hero-image-container');
    if (heroImage) {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrolled = window.pageYOffset;
                    const heroSection = document.querySelector('.hero');
                    if (heroSection) {
                        const heroHeight = heroSection.offsetHeight;
                        if (scrolled < heroHeight) {
                            const rate = scrolled * 0.2;
                            heroImage.style.transform = `translateY(${rate}px)`;
                        }
                    }
                    ticking = false;
                });
                ticking = true;
            }
        });
    }
});

// Service Card Hover Effects
document.querySelectorAll('.service-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        const priceElement = card.querySelector('.service-price');
        if (priceElement) {
            priceElement.style.transform = 'scale(1.05)';
            priceElement.style.transition = 'transform 0.3s ease';
        }
    });
    
    card.addEventListener('mouseleave', () => {
        const priceElement = card.querySelector('.service-price');
        if (priceElement) {
            priceElement.style.transform = 'scale(1)';
        }
    });
});

// Radio Button Custom Styling
document.querySelectorAll('.radio-input').forEach(radio => {
    radio.addEventListener('change', function() {
        // Remove checked state from all radios in the same group
        document.querySelectorAll(`input[name="${this.name}"]`).forEach(r => {
            r.closest('.radio-label').classList.remove('selected');
        });
        
        // Add selected class to current radio
        this.closest('.radio-label').classList.add('selected');
    });
});

// Hero Goal Cards - Selection and Redirect to Bot
document.addEventListener('DOMContentLoaded', () => {
    const goalCards = document.querySelectorAll('.goal-card');
    const heroCta = document.getElementById('heroCtaBtn');
    let selectedGoal = null;
    
    // Telegram Bot Username
    const BOT_USERNAME = 'levelfitbot';
    
    goalCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove selected class from all cards
            goalCards.forEach(c => c.classList.remove('selected'));
            
            // Add selected class to clicked card
            card.classList.add('selected');
            
            // Save selected goal
            selectedGoal = card.getAttribute('data-goal');
            const goalTitle = card.querySelector('.goal-card-title')?.textContent;
            console.log('Выбрана цель:', goalTitle, '(', selectedGoal, ')');
            
            // Scroll to button smoothly
            if (heroCta) {
                const buttonPosition = heroCta.getBoundingClientRect().top + window.pageYOffset;
                const offset = window.innerHeight / 2 - heroCta.offsetHeight / 2;
                
                window.scrollTo({
                    top: buttonPosition - offset,
                    behavior: 'smooth'
                });
                
                // Add pulse animation to CTA button after scroll
                setTimeout(() => {
                    heroCta.classList.add('btn-pulse');
                    setTimeout(() => {
                        heroCta.classList.remove('btn-pulse');
                    }, 1000);
                }, 500);
            }
        });
    });
    
    // CTA button redirects to Telegram bot with selected goal
    if (heroCta) {
        heroCta.addEventListener('click', () => {
            if (selectedGoal) {
                // Get current currency
                const currentCurrency = localStorage.getItem('selectedCurrency') || DEFAULT_CURRENCY;
                
                // Redirect to Telegram bot with goal and currency parameters
                const telegramUrl = `https://t.me/${BOT_USERNAME}?start=${selectedGoal}_${currentCurrency}`;
                window.open(telegramUrl, '_blank');
            } else {
                // If no goal selected, show alert
                alert('Пожалуйста, выберите цель тренировок');
            }
        });
    }
});

// Before/After Slider Functionality
document.addEventListener('DOMContentLoaded', () => {
    const resultCards = document.querySelectorAll('.result-card');
    
    resultCards.forEach(card => {
        const container = card.querySelector('.result-image-container');
        const slider = card.querySelector('.result-slider');
        const handle = card.querySelector('.result-slider-handle');
        
        if (!container || !slider || !handle) return;
        
        let rafId = null;
        
        // Function to update slider position
        function updateSliderPosition(percentage) {
            // Cancel any pending animation frame
            if (rafId) {
                cancelAnimationFrame(rafId);
            }
            
            // Use requestAnimationFrame for smooth updates
            rafId = requestAnimationFrame(() => {
                container.style.setProperty('--slider-position', percentage + '%');
                handle.style.left = percentage + '%';
                rafId = null;
            });
        }
        
        // Handle slider input
        slider.addEventListener('input', (e) => {
            const value = e.target.value;
            updateSliderPosition(value);
        });
        
        // Handle mouse drag on container
        let isDragging = false;
        
        function handleMove(e) {
            if (!isDragging) return;
            
            const rect = container.getBoundingClientRect();
            let x;
            
            if (e.type.startsWith('touch')) {
                x = e.touches[0].clientX - rect.left;
            } else {
                x = e.clientX - rect.left;
            }
            
            const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
            slider.value = percentage;
            updateSliderPosition(percentage);
        }
        
        function startDrag(e) {
            e.preventDefault(); // Prevent text selection
            isDragging = true;
            container.style.cursor = 'grabbing';
            handleMove(e);
        }
        
        function stopDrag() {
            isDragging = false;
            container.style.cursor = 'grab';
        }
        
        // Mouse events
        container.addEventListener('mousedown', startDrag);
        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', stopDrag);
        
        // Touch events for mobile
        container.addEventListener('touchstart', (e) => {
            isDragging = true;
            handleMove(e);
        });
        
        document.addEventListener('touchmove', handleMove);
        document.addEventListener('touchend', stopDrag);
        
        // Initialize position
        updateSliderPosition(50);
    });
});

// Currency Switcher Functionality
document.addEventListener('DOMContentLoaded', () => {
    const currencyButtons = document.querySelectorAll('.currency-btn');
    
    // Get saved currency from localStorage or use default
    let currentCurrency = localStorage.getItem('selectedCurrency') || DEFAULT_CURRENCY;
    
    // Update all prices on the page
    function updateAllPrices(currency) {
        currentCurrency = currency;
        
        // Update all subscription cards
        document.querySelectorAll('.subscription-price').forEach(priceElement => {
            const usdPrice = parseFloat(priceElement.getAttribute('data-usd-price'));
            if (usdPrice) {
                const convertedPrice = convertPrice(usdPrice, currency);
                priceElement.textContent = formatPrice(convertedPrice, currency);
            }
        });
        
        // Update all old prices
        document.querySelectorAll('.subscription-price-old').forEach(priceElement => {
            const usdPrice = parseFloat(priceElement.getAttribute('data-usd-price'));
            if (usdPrice) {
                const convertedPrice = convertPrice(usdPrice, currency);
                priceElement.textContent = formatPrice(convertedPrice, currency);
            }
        });
        
        // Save to localStorage
        localStorage.setItem('selectedCurrency', currency);
    }
    
    // Set active button based on current currency
    function setActiveButton(currency) {
        const indicator = document.querySelector('.currency-slider-indicator');
        
        currencyButtons.forEach(btn => {
            if (btn.getAttribute('data-currency') === currency) {
                btn.classList.add('active');
                
                // Move the slider indicator
                const index = parseInt(btn.getAttribute('data-index'));
                if (indicator) {
                    indicator.style.transform = `translateX(${index * 100}%)`;
                }
            } else {
                btn.classList.remove('active');
            }
        });
    }
    
    // Add click handlers to currency buttons
    currencyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const selectedCurrency = button.getAttribute('data-currency');
            updateAllPrices(selectedCurrency);
            setActiveButton(selectedCurrency);
        });
    });
    
    // Initialize with saved or default currency
    updateAllPrices(currentCurrency);
    setActiveButton(currentCurrency);
});
