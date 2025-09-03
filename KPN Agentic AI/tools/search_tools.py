from langchain_core.tools import tool
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

def search_kpn_products(query: str) -> str:
    """Search for KPN products using semantic search (RAG)."""
    try:
        if not vector_store_manager.kpn_vector_store:
            return "KPN vector store not initialized."
        
        results = vector_store_manager.kpn_vector_store.similarity_search_with_score(query, k=3)
        
        if not results:
            return "No KPN products found matching your query."
        
        response = f"📱 Found {len(results)} KPN products:\n\n"
        for i, (doc, score) in enumerate(results, 1):
            metadata = doc.metadata
            response += f"{i}. {metadata['product_name']}\n"
            response += f"   Price: €{metadata['price']}\n"
            if metadata.get('monthly_price', 0) > 0:
                response += f"   Monthly: €{metadata['monthly_price']} ({metadata['contract_type']})\n"
            if metadata.get('kpn_exclusive', False):
                response += f"   🌟 KPN Exclusive Deal!\n"
            response += f"   Relevance: {score:.2f}\n\n"
        
        return response
        
    except Exception as e:
        return f"Error searching KPN products: {str(e)}"

def search_external_products(query: str) -> str:
    """Search for products from external sources using semantic search (RAG)."""
    try:
        if not vector_store_manager.external_vector_store:
            return "External vector store not initialized."
        
        results = vector_store_manager.external_vector_store.similarity_search_with_score(query, k=3)
        
        if not results:
            return "No external products found matching your query."
        
        response = f"🌐 Found {len(results)} products from external sources:\n\n"
        for i, (doc, score) in enumerate(results, 1):
            metadata = doc.metadata
            response += f"{i}. {metadata['product_name']}\n"
            response += f"   Brand: {metadata['brand']}\n"
            response += f"   Price: €{metadata['price']}\n"
            response += f"   Relevance: {score:.2f}\n\n"
        
        return response
        
    except Exception as e:
        return f"Error searching external products: {str(e)}"

def compare_with_market(query: str) -> str:
    """Compare KPN products with broader market offerings using hybrid RAG search."""
    try:
        if not vector_store_manager.hybrid_vector_store:
            return "Hybrid vector store not initialized."
        
        results = vector_store_manager.hybrid_vector_store.similarity_search_with_score(query, k=6)
        
        # Separate KPN and external results
        kpn_results = [(doc, score) for doc, score in results if doc.metadata['source'] == 'kpn']
        external_results = [(doc, score) for doc, score in results if doc.metadata['source'] == 'external']
        
        response = f"📊 Market Comparison for '{query}':\n\n"
        
        # KPN Results
        if kpn_results:
            response += "📱 KPN Products:\n"
            for i, (doc, score) in enumerate(kpn_results[:2], 1):
                metadata = doc.metadata
                response += f"• {metadata['product_name']} - €{metadata['price']}"
                if metadata.get('kpn_exclusive', False):
                    response += " 🌟"
                response += "\n"
            response += "\n"
        
        # External Results
        if external_results:
            response += "🌐 Market Comparison:\n"
            for i, (doc, score) in enumerate(external_results[:2], 1):
                metadata = doc.metadata
                response += f"• {metadata['product_name']} - €{metadata['price']}\n"
            response += "\n"
        
        # Value proposition
        if kpn_results and external_results:
            kpn_prices = [doc.metadata['price'] for doc, score in kpn_results]
            ext_prices = [doc.metadata['price'] for doc, score in external_results]
            
            if kpn_prices and ext_prices:
                avg_kpn = sum(kpn_prices) / len(kpn_prices)
                avg_ext = sum(ext_prices) / len(ext_prices)
                
                if avg_kpn <= avg_ext * 1.1:
                    response += "💡 KPN offers competitive pricing with added service benefits!"
                else:
                    response += "💡 Consider KPN's exclusive deals and customer service value."
        
        return response
        
    except Exception as e:
        return f"Error performing market comparison: {str(e)}"

def check_kpn_exclusive_deals(query: str) -> str:
    """Check for KPN exclusive deals and offers."""
    try:
        if not vector_store_manager.kpn_vector_store:
            return "KPN vector store not initialized."
        
        exclusive_query = f"KPN exclusive deals {query}"
        results = vector_store_manager.kpn_vector_store.similarity_search_with_score(exclusive_query, k=5)
        
        # Filter for exclusive deals
        exclusive_results = [(doc, score) for doc, score in results if doc.metadata.get('kpn_exclusive', False)]
        
        if not exclusive_results:
            return "Currently no exclusive deals found, but here are relevant KPN products:\n\n" + search_kpn_products(query)
        
        response = "🌟 KPN Exclusive Deals:\n\n"
        for i, (doc, score) in enumerate(exclusive_results[:3], 1):
            metadata = doc.metadata
            response += f"{i}. {metadata['product_name']}\n"
            response += f"   Price: €{metadata['price']}\n"
            if metadata.get('monthly_price', 0) > 0:
                response += f"   Monthly: €{metadata['monthly_price']} ({metadata['contract_type']})\n"
            response += f"   Special KPN pricing and offers!\n\n"
        
        return response
        
    except Exception as e:
        return f"Error checking exclusive deals: {str(e)}"