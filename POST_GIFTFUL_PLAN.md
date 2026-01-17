# BuyHive — Product Roadmap 🚀

> Strategic roadmap: From current state to buying-first platform
> 
> **Status**: Reference Document (Internal Use Only)
> **Created**: 2025
> **Vision**: BuyHive is the operating system for purchasing items across the internet

---

## 🎯 Vision & Positioning

**BuyHive is a cross-store shopping platform that helps users save, organize, and purchase items from any online retailer.**

**Core Focus**: Making buying better, not wishlisting
- Buying efficiency over gifting
- Purchase readiness over long-term saving
- Checkout optimization over social features

**Key Distinction**:
- Giftful = Wishlist/gifting platform (social, claiming, long-term)
- BuyHive = Shopping cart platform (personal, buying, immediate)

---

## 📐 Architecture Overview

### Current Architecture
- **Extension**: Handles extraction + some logic
- **Backend**: API for cart/item management
- **Website**: (Current state unclear)

### Target Architecture

**BuyHive Website** (Primary Interface)
- All cart/item management
- Cart organization and editing
- Checkout assistance
- Price tracking
- User dashboard

**Browser Extension** (Extraction Tool)
- **Primary role**: Extract item info from e-commerce sites
- Send extracted data to backend
- Minimal UI (extraction popup only)
- Lightweight and focused

**Backend API** (Logic Layer)
- Cart/item management
- Item extraction processing
- AI verification and enhancement
- Price tracking
- Email sharing

**Flow**:
```
User browses → Extension extracts → Backend processes → Website displays/manages
                                                         ↓
                                    User manages on website → Buy button → Checkout
```

---

## 🗺️ Roadmap Phases

### Phase 1: Foundation & Polish (Current → Giftful-Level UX)

**Goal**: Reach polished, trustworthy UX while maintaining buying focus

**Timeline**: 2-3 months

#### Core Features

##### 1.1 Universal Item Saving ✅ (You Have This)
- [x] Browser extension for extraction
- [x] AI-powered extraction (Groq/OpenAI)
- [x] Image verification (CLIP + OpenAI Vision)
- [x] URL classification (BERT)
- [ ] Polish: Better error handling
- [ ] Polish: Confidence scores for extractions

##### 1.2 Cart Management ✅ (You Have This)
- [x] Multiple carts
- [x] Create, edit, delete carts
- [x] Item organization
- [x] Notes on items
- [ ] Polish: Better cart organization UI
- [ ] Enhancement: Cart templates (e.g., "Weekly Shopping", "Tech")

##### 1.3 User Accounts ✅ (You Have This)
- [x] Auth0 authentication
- [x] User profiles
- [x] Cart/item persistence
- [ ] Polish: Profile settings page
- [ ] Enhancement: Account preferences

##### 1.4 Email Sharing ✅ (You Have This)
- [x] Share carts via email
- [x] Email templates
- [ ] Polish: Better email formatting
- [ ] Enhancement: Share specific items (not just full cart)

##### 1.5 Price Tracking (New)
**Priority**: High | **Complexity**: Medium

**Features**:
- Track price history for items
- Store price changes over time
- Basic price alerts (notifications when price drops)

**Implementation**:
```python
# New Collection: PriceHistory
{
    "item_id": str,
    "price": float,
    "currency": str,
    "retailer": str,
    "timestamp": datetime,
    "url": str
}

# Service: Daily price tracking (cron job)
# Endpoint: GET /items/{item_id}/price-history
# Frontend: Price chart/trend display
```

**Why**: Essential for buying decisions (know when to buy)

##### 1.6 Website Dashboard (New - Critical)
**Priority**: Critical | **Complexity**: High

**What's Needed**:
- Full-featured web application
- Cart management interface
- Item organization UI
- Price tracking display
- User settings

**Why**: Extension should be extraction-only. All management happens on website.

**Features**:
- View all carts
- Edit cart names/items
- Organize items
- Price history viewer
- Settings/preferences

##### 1.7 Extension Refactor (New - Critical)
**Priority**: Critical | **Complexity**: Medium

**Current**: Extension handles some logic
**Target**: Extension is extraction-focused

**Changes Needed**:
- Remove cart management from extension
- Keep only extraction popup
- Send extracted data to backend
- Redirect to website after extraction

**Why**: Centralize logic on website, keep extension lightweight

#### Phase 1 Deliverables

- [ ] Polished website dashboard
- [ ] Refactored extension (extraction-only)
- [ ] Price tracking system
- [ ] Better error handling
- [ ] Improved UX/UI throughout
- [ ] Email sharing enhancements

**Success Criteria**:
- Website is primary interface
- Extension is lightweight extraction tool
- Polished, trustworthy UX
- Users can efficiently manage carts
- Ready for Phase 2 features

---

### Phase 2: Buying Intelligence & Checkout Assistance

**Goal**: Transform from passive saving to active buying support

**Timeline**: 2-3 months after Phase 1

#### Core Features

##### 2.1 Retailer Grouping
**Priority**: High | **Complexity**: Low

**Features**:
- Automatically group items by retailer
- Display subtotal per retailer
- Display total across all retailers
- Visual organization by store

**Implementation**:
```python
# Backend: Group items by domain
GET /carts/{cart_id}/grouped-by-retailer

# Returns:
{
    "retailers": {
        "amazon.com": {
            "items": [...],
            "subtotal": 150.00,
            "currency": "USD"
        },
        "target.com": {
            "items": [...],
            "subtotal": 75.50
        }
    },
    "total": 225.50
}
```

**Why**: Essential for multi-retailer checkout

##### 2.2 Smart Buy Button
**Priority**: High | **Complexity**: Medium-High

**Features**:
- "Buy Now" button on carts
- Opens retailer sites with items
- Best-effort cart automation
- Fallback to manual lists

**Implementation Approach**:

**Backend**:
```python
GET /carts/{cart_id}/buy-links
# Returns: Items grouped by retailer with URLs
```

**Frontend (Website)**:
```javascript
// User clicks "Buy Now"
1. Fetch buy links (grouped by retailer)
2. For each retailer:
   - Open retailer site in new tab
   - If automation supported:
     * Use browser extension helper script
     * Try to add items to cart automatically
   - If not:
     * Show items list overlay
     * User manually adds items
3. User completes checkout on retailer site
```

**Browser Extension Helper** (Optional Enhancement):
- Content script that can add items to cart
- Works on retailers that don't block automation
- Injects "Add to Cart" buttons for items from BuyHive

**Technical Reality**:
- Some retailers support automation (can add items programmatically)
- Many retailers block automation (anti-bot measures)
- Fallback: Clear item list per retailer, user adds manually
- Still faster than manual browsing

**Why**: Core buying feature - makes multi-retailer checkout easier

##### 2.3 Price Intelligence
**Priority**: High | **Complexity**: Medium

**Features**:
- AI-powered price analysis
- "Good deal" indicators
- Price drop predictions
- Cheaper alternative suggestions

**Implementation**:
```python
# AI analyzes price trends
POST /items/{item_id}/analyze-price
# Returns: Is this a good deal? Predicted price drops? Alternatives?
```

**Why**: Helps users decide when to buy

##### 2.4 Checkout Optimization
**Priority**: Medium | **Complexity**: Medium

**Features**:
- Suggest optimal checkout order (e.g., free shipping first)
- Estimate shipping costs
- Calculate total savings
- Checkout timeline/plan

**Why**: Makes multi-retailer checkout more efficient

#### Phase 2 Deliverables

- [ ] Retailer grouping system
- [ ] Smart buy button (with automation where possible)
- [ ] Price intelligence features
- [ ] Checkout optimization
- [ ] Browser extension helper (optional)

**Success Criteria**:
- Users can efficiently checkout across multiple retailers
- Price intelligence helps buying decisions
- Checkout flow is optimized
- Ready for Phase 3 (if desired)

---

### Phase 3: Advanced Buying Features (Optional Future)

**Goal**: Ultimate buying platform

**Timeline**: 6+ months (after Phase 2 proves successful)

#### Potential Features

##### 3.1 Proxy Purchasing
- Users pay BuyHive
- BuyHive purchases items on their behalf
- Single payment, multiple retailers

**Complexity**: Very High
**Why**: Ultimate differentiator, but complex legally/operationally

##### 3.2 Purchase History & Analytics
- Track what users actually bought
- Spending analytics
- Purchase patterns

##### 3.3 Smart Reordering
- Remember frequently bought items
- One-click reorder

##### 3.4 Advanced Price Intelligence
- Price predictions
- Optimal buying timing
- Automated price monitoring

**Note**: Phase 3 is optional. Focus on Phase 1 & 2 first.

---

## 🚫 What BuyHive is NOT (Phase 1-2)

- ❌ **NOT a wishlist/gifting platform** (that's Giftful)
- ❌ **NOT social-first** (no friends/following)
- ❌ **NOT claiming-based** (no anonymous claiming)
- ❌ **NOT payment processor** (Phase 1-2)
- ❌ **NOT a gift registry** (focused on buying, not gifting)

---

## 🏗️ Architecture Changes Needed

### Current State
- Extension: Some logic + extraction
- Backend: API for management
- Website: (Need to clarify/develop)

### Target State

**BuyHive Website** (Primary)
- React/Next.js or similar
- Full cart/item management
- Dashboard
- Settings
- Checkout assistance UI

**Browser Extension** (Extraction Tool)
- Minimal UI (extraction popup)
- Extract item info
- Send to backend
- Redirect to website after extraction
- Optional: Helper script for buy button

**Backend API** (Current - Enhanced)
- Keep current structure
- Add price tracking
- Add retailer grouping
- Add buy links endpoint
- Email sharing (already exists)

**Data Flow**:
```
Extension (Extraction) → Backend (Process) → Website (Display/Manage)
                                                ↓
                                    Buy Button → Retailer Sites → Checkout
```

---

## 📋 Implementation Checklist

### Phase 1 Priority Order

**Week 1-2: Website Foundation**
- [ ] Build/improve website dashboard
- [ ] Cart management UI
- [ ] Item organization UI
- [ ] User settings page

**Week 3-4: Extension Refactor**
- [ ] Simplify extension (extraction-only)
- [ ] Remove cart management from extension
- [ ] Streamline extraction flow
- [ ] Redirect to website after extraction

**Week 5-6: Price Tracking**
- [ ] Price history database schema
- [ ] Price tracking service (cron job)
- [ ] Price history API endpoints
- [ ] Price chart UI

**Week 7-8: Polish & UX**
- [ ] Error handling improvements
- [ ] UI/UX polish
- [ ] Email sharing enhancements
- [ ] Testing and bug fixes

### Phase 2 Priority Order

**Week 1-2: Retailer Grouping**
- [ ] Backend: Group items by retailer
- [ ] Frontend: Retailer grouping display
- [ ] Subtotal calculations

**Week 3-5: Smart Buy Button**
- [ ] Buy links API endpoint
- [ ] Frontend: Buy button UI
- [ ] Multi-tab opening logic
- [ ] Browser automation (where possible)
- [ ] Fallback manual lists

**Week 6-8: Price Intelligence**
- [ ] Price analysis AI service
- [ ] Good deal indicators
- [ ] Price predictions
- [ ] Alternative suggestions

**Week 9-10: Checkout Optimization**
- [ ] Checkout order optimization
- [ ] Shipping estimates
- [ ] Savings calculations
- [ ] Checkout timeline

---

## 🎯 Success Metrics

### Phase 1 Success
- Website is primary interface
- Extension is lightweight and focused
- Polished UX throughout
- Price tracking working
- Users can efficiently manage carts

### Phase 2 Success
- Users can checkout across multiple retailers
- Buy button reduces checkout time
- Price intelligence helps buying decisions
- Users complete purchases successfully

---

## 💡 Key Principles

1. **Buying-First**: Every feature should support buying efficiency
2. **Website-Centric**: Website is primary interface
3. **Extension-Lightweight**: Extension is extraction tool only
4. **No Social**: Skip social features (except email sharing)
5. **Realistic**: Set achievable goals, iterate based on feedback

---

## 📝 Notes

- **Extension Role**: Should be lightweight extraction tool, not full management interface
- **Website Role**: All cart/item management happens here
- **Social Features**: Skip for now (can add later if needed)
- **Giftful-Level**: Means polished UX, not feature parity (we're different product)
- **Checkout Assistance**: Best-effort automation, fallback to manual
- **Flexibility**: Plan can evolve based on user feedback

---

**Last Updated**: 2025
**Status**: Active Roadmap
**Next Review**: After Phase 1 completion
