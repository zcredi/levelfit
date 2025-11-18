// Mobile Menu Toggle
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('.nav-menu');

menuToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
    });
});

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Subscription Plans Data
const plans = {
    workouts: {
        name: 'Тренировки',
        price: 1990,
        description: 'Базовый план с доступом к тренировкам'
    },
    nutrition: {
        name: 'Питание',
        price: 1490,
        description: 'План питания с персональными рекомендациями'
    },
    'workouts-nutrition': {
        name: 'Тренировки + Питание',
        price: 2990,
        description: 'Комплексный план тренировок и питания'
    },
    premium: {
        name: 'Всё включено',
        price: 4990,
        description: 'Премиум план с полной поддержкой тренера'
    }
};

// Modal Elements
const modal = document.getElementById('subscriptionModal');
const modalPlanName = document.getElementById('modalPlanName');
const modalPrice = document.getElementById('modalPrice');
const subscriptionForm = document.getElementById('subscriptionForm');
const modalClose = document.querySelector('.modal-close');

// Open Modal on Subscribe Button Click
document.querySelectorAll('.btn-subscribe').forEach(button => {
    button.addEventListener('click', () => {
        const planId = button.getAttribute('data-plan');
        const plan = plans[planId];
        
        if (plan) {
            modalPlanName.textContent = plan.name;
            modalPrice.textContent = `${plan.price} ₽/месяц`;
            subscriptionForm.setAttribute('data-plan', planId);
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    });
});

// Close Modal
modalClose.addEventListener('click', () => {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
});

// Close Modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// Handle Form Submission
subscriptionForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const formData = new FormData(subscriptionForm);
    const planId = subscriptionForm.getAttribute('data-plan');
    const plan = plans[planId];
    
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
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
});

// Navbar Background on Scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(10, 10, 10, 0.98)';
    } else {
        navbar.style.background = 'rgba(10, 10, 10, 0.95)';
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
    const animatedElements = document.querySelectorAll('.feature-card, .subscription-card, .gallery-item, .contact-item');
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Price Animation on Hover
document.querySelectorAll('.subscription-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        const priceAmount = card.querySelector('.price-amount');
        if (priceAmount) {
            priceAmount.style.transform = 'scale(1.1)';
            priceAmount.style.transition = 'transform 0.3s ease';
        }
    });
    
    card.addEventListener('mouseleave', () => {
        const priceAmount = card.querySelector('.price-amount');
        if (priceAmount) {
            priceAmount.style.transform = 'scale(1)';
        }
    });
});

