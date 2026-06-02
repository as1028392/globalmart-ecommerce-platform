import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Truck, Shield, Clock, Globe } from 'lucide-react';
import { ProductGrid } from '../components/ProductCard';
import { productAPI } from '../services/api';

export const HomePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState(searchParams.get('category') || 'all');

  useEffect(() => {
    const fetchProducts = async () => {
      setIsLoading(true);
      try {
        const params: any = {};
        if (activeCategory !== 'all') params.category = activeCategory;
        const response = await productAPI.getProducts(params);
        setProducts(response.data.products);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProducts();
  }, [activeCategory]);

  const categories = [
    { id: 'all', name: 'All Products' },
    { id: 'textile', name: 'Turkish Textile' },
    { id: 'beauty', name: 'Korean Beauty' },
    { id: 'electronics', name: 'Electronics' },
    { id: 'home', name: 'Home & Living' },
    { id: 'fashion', name: 'Fashion' },
  ];

  return (
    <div>
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1920')] bg-cover bg-center opacity-20" />
        <div className="relative max-w-7xl mx-auto px-4 py-24">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="max-w-2xl"
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Shop Global.<br />
              <span className="text-blue-300">Pay Local.</span>
            </h1>
            <p className="text-xl text-blue-100 mb-8">
              Access millions of products from Turkey, Korea, and China with transparent pricing in EGP. No hidden fees.
            </p>
            <div className="flex flex-wrap gap-4">
              <button className="bg-white text-blue-900 px-8 py-4 rounded-xl font-bold hover:bg-blue-50 transition-colors">
                Start Shopping
              </button>
              <button className="border-2 border-white text-white px-8 py-4 rounded-xl font-bold hover:bg-white/10 transition-colors">
                How It Works
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { icon: Globe, title: 'Global Sources', desc: 'Turkey, Korea, China' },
              { icon: Shield, title: 'Secure Payment', desc: 'Vodafone Cash & Cards' },
              { icon: Truck, title: 'Door Delivery', desc: 'Bosta & Aramex' },
              { icon: Clock, title: 'Real-time Pricing', desc: 'Live exchange rates' },
            ].map((badge) => (
              <div key={badge.title} className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600">
                  <badge.icon size={24} />
                </div>
                <div>
                  <p className="font-semibold text-sm">{badge.title}</p>
                  <p className="text-xs text-gray-500">{badge.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold">Featured Products</h2>
          <div className="hidden md:flex items-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  activeCategory === cat.id
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        <div className="md:hidden mb-6 overflow-x-auto">
          <div className="flex gap-2 pb-2">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  activeCategory === cat.id
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-gray-100 rounded-2xl h-96 animate-pulse" />
            ))}
          </div>
        ) : (
          <ProductGrid products={products} />
        )}
      </section>
    </div>
  );
};
