# 🚀 QuantAnalytics SaaS Setup Guide

## 🎯 **What We've Built**

Your AI BI Dashboard has been transformed into a **production-ready SaaS platform** with:

### ✅ **Core SaaS Features**
- **Multi-tenant architecture** with organizations
- **Subscription management** with Stripe integration
- **Usage tracking & rate limiting** per plan
- **Role-based permissions** (Owner, Admin, Member, Viewer)
- **Admin dashboard** for platform management
- **Billing & invoice management**

### 💰 **Subscription Tiers**
- **🆓 Starter** ($0/month): 5 datasets, 1 dashboard, 100 API calls
- **💼 Professional** ($49/month): 100 datasets, 10 dashboards, 10K API calls, Advanced Analytics
- **🏢 Enterprise** ($199/month): Unlimited everything, Custom Models, SSO, White-label

## 🛠️ **Setup Instructions**

### 1. **Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. **Install Dependencies**
```bash
# Backend dependencies
cd BI_board
pip install -r requirements.txt

# Frontend dependencies  
cd ../board_ui
npm install
```

### 3. **Database Setup**
```bash
# Run migrations
cd BI_board
python manage.py migrate

# Create subscription plans
python manage.py create_subscription_plans

# Create superuser
python manage.py createsuperuser
```

### 4. **Stripe Configuration**
1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe dashboard
3. Add keys to your `.env` file:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
4. Set up webhook endpoint: `https://yourdomain.com/api/webhooks/stripe/`

### 5. **Redis Setup**
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### 6. **Run the Application**

#### Development Mode:
```bash
# Terminal 1: Django backend
cd BI_board
python manage.py runserver

# Terminal 2: Celery worker
celery -A BI_board worker -l info

# Terminal 3: React frontend
cd board_ui
npm run dev
```

#### Production Mode (Docker):
```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🔧 **Key Configuration Files**

### **Backend Configuration**
- `apps/organizations/models.py` - SaaS data models
- `apps/organizations/middleware.py` - Usage tracking & rate limiting
- `apps/organizations/permissions.py` - Role-based access control
- `BI_board/settings.py` - Updated with SaaS settings

### **Frontend Components**
- `OrganizationDashboard.jsx` - Organization overview & usage
- `BillingPage.jsx` - Subscription management
- `AdminDashboard.jsx` - Platform-wide analytics

## 📊 **New API Endpoints**

### **Organizations**
- `GET /api/organizations/` - List user's organizations
- `POST /api/organizations/` - Create new organization
- `GET /api/organizations/{id}/usage_analytics/` - Usage data

### **Billing**
- `GET /api/billing/{org_id}/` - Billing information
- `POST /api/billing/create-checkout-session/` - Stripe checkout
- `POST /api/webhooks/stripe/` - Stripe webhooks

### **Admin**
- `GET /api/admin/dashboard/` - Platform metrics
- `GET /api/admin/usage-analytics/` - Usage analytics
- `GET /api/admin/billing/` - Revenue analytics

## 🚀 **Deployment Checklist**

### **Pre-Production**
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Set up Stripe webhooks
- [ ] Configure email settings
- [ ] Set up SSL certificates

### **Production Environment**
- [ ] Use Docker Compose for orchestration
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure monitoring (Sentry, New Relic)
- [ ] Set up backup strategy
- [ ] Configure auto-scaling
- [ ] Set up CI/CD pipeline

## 🔐 **Security Features**

- **JWT Authentication** with refresh tokens
- **Rate limiting** per subscription tier
- **CORS protection** for API endpoints
- **SQL injection protection** via Django ORM
- **XSS protection** with Django middleware
- **CSRF protection** for forms

## 📈 **Monitoring & Analytics**

### **Built-in Metrics**
- User registration & activity
- API usage per organization
- Revenue tracking
- Subscription conversions
- Error rates & performance

### **Usage Tracking**
- Automatic usage logging
- Real-time rate limiting
- Monthly quota enforcement
- Billing period tracking

## 🎨 **Customization Options**

### **Branding**
- Update logo in `board_ui/src/assets/`
- Modify colors in `tailwind.config.js`
- Customize email templates

### **Features**
- Add new subscription plans in Django admin
- Create custom ML models for Enterprise
- Implement SSO providers (Google, Microsoft)
- Add white-label options

## 🆘 **Troubleshooting**

### **Common Issues**
1. **Stripe webhooks failing**: Check webhook URL and secret
2. **Rate limiting too strict**: Adjust limits in middleware
3. **Database migrations**: Run `python manage.py migrate`
4. **Redis connection**: Ensure Redis is running
5. **CORS errors**: Update `CORS_ALLOWED_ORIGINS` in settings

### **Logs to Check**
- Django: `docker-compose logs backend`
- Celery: `docker-compose logs celery`
- Frontend: `docker-compose logs frontend`
- Database: `docker-compose logs db`

## 🎯 **Next Steps**

1. **Test the complete flow**: Signup → Subscribe → Use features
2. **Set up monitoring**: Add Sentry for error tracking
3. **Configure backups**: Database and media files
4. **Marketing site**: Create landing pages
5. **Documentation**: API docs with Swagger
6. **Mobile app**: React Native or Flutter

## 💡 **Revenue Optimization**

- **Free trial**: 14-day trial for Professional plan
- **Usage alerts**: Notify users approaching limits
- **Upgrade prompts**: Show upgrade options when limits reached
- **Annual discounts**: 2 months free for yearly plans
- **Enterprise sales**: Custom pricing for large organizations

---

**🎉 Congratulations!** Your AI BI Dashboard is now a **production-ready SaaS platform**!

For support, check the logs or create an issue in the repository.
