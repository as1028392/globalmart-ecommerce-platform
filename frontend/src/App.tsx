import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { Search, Menu, X, User, Heart } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { CartIcon, SmartCart } from './components/SmartCart';
import { CheckoutPage } from './pages/CheckoutPage';
import { OrderTrackingPage } from './pages/TrackingPage';
import { OrderSuccessPage } from './pages/OrderSuccessPage';
import { HomePage } from './pages/HomePage';
import { ProductDetailPage } from './pages/ProductDetailPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const Navbar: React.FC = () => {
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <>
      <nav className="sticky top-0 z-40 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">G</span>
              </div>
              <span className="text-xl font-bold hidden sm:block">GlobalMart</span>
            </Link>

            <div className="flex-1 max-w-xl mx-8 hidden md:block">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search products..."
                  className="w-full pl-10 pr-4 py-2.5 bg-gray-100 rounded-xl focus:bg-white focus:ring-2 focus:ring-blue-200 transition-all"
                />
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors md:hidden">
                <Search size={20} />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors hidden sm:block">
                <Heart size={20} />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors hidden sm:block">
                <User size={20} />
              </button>
              <CartIcon onClick={() => setIsCartOpen(true)} />
              <button
                className="p-2 hover:bg-gray-100 rounded-full transition-colors lg:hidden"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
            </div>
          </div>
        </div>

        <div className="hidden lg:block border-t border-gray-100">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center gap-8 h-12 text-sm font-medium text-gray-600">
              <Link to="/?category=textile" className="hover:text-blue-600 transition-colors">Turkish Textile</Link>
              <Link to="/?category=beauty" className="hover:text-blue-600 transition-colors">Korean Beauty</Link>
              <Link to="/?category=electronics" className="hover:text-blue-600 transition-colors">Electronics</Link>
              <Link to="/?category=home" className="hover:text-blue-600 transition-colors">Home & Living</Link>
              <Link to="/?category=fashion" className="hover:text-blue-600 transition-colors">Fashion</Link>
              <Link to="/?category=general" className="hover:text-blue-600 transition-colors">AliExpress Deals</Link>
            </div>
          </div>
        </div>
      </nav>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-white border-b border-gray-100 overflow-hidden"
          >
            <div className="p-4 space-y-3">
              <Link to="/?category=textile" className="block py-2 font-medium">Turkish Textile</Link>
              <Link to="/?category=beauty" className="block py-2 font-medium">Korean Beauty</Link>
              <Link to="/?category=electronics" className="block py-2 font-medium">Electronics</Link>
              <Link to="/?category=home" className="block py-2 font-medium">Home & Living</Link>
              <Link to="/?category=fashion" className="block py-2 font-medium">Fashion</Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <SmartCart isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </>
  );
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-white">
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/product/:id" element={<ProductDetailPage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
              <Route path="/track/:trackingNumber" element={<OrderTrackingPage />} />
              <Route path="/order-success/:orderNumber" element={<OrderSuccessPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
        <Toaster position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const Footer: React.FC = () => (
  <footer className="bg-gray-900 text-gray-300 py-12 mt-20">
    <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
      <div>
        <h3 className="text-white font-bold text-lg mb-4">GlobalMart</h3>
        <p className="text-sm">Your gateway to global markets. Shop from Turkey, Korea, China and more with transparent pricing and local delivery.</p>
      </div>
      <div>
        <h4 className="text-white font-semibold mb-4">Shop</h4>
        <ul className="space-y-2 text-sm">
          <li><Link to="/?category=textile" className="hover:text-white transition-colors">Turkish Textile</Link></li>
          <li><Link to="/?category=beauty" className="hover:text-white transition-colors">Korean Beauty</Link></li>
          <li><Link to="/?category=electronics" className="hover:text-white transition-colors">Electronics</Link></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-semibold mb-4">Support</h4>
        <ul className="space-y-2 text-sm">
          <li><Link to="/track" className="hover:text-white transition-colors">Track Order</Link></li>
          <li><a href="#" className="hover:text-white transition-colors">Shipping Info</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Returns</a></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-semibold mb-4">Contact</h4>
        <ul className="space-y-2 text-sm">
          <li>Email: support@globalmart.com</li>
          <li>Phone: 190XX</li>
          <li>Cairo, Egypt</li>
        </ul>
      </div>
    </div>
    <div className="max-w-7xl mx-auto px-4 mt-8 pt-8 border-t border-gray-800 text-sm text-center">
      © 2024 GlobalMart. All rights reserved.
    </div>
  </footer>
);

export default App;
