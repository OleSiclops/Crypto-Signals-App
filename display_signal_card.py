
import streamlit as st

def display_signal_card(signal):
    buy_score = signal['buy_score']
    name = signal['name']
    symbol = signal['symbol']
    price = signal['current_price']
    entry_low = signal['buy_range'][0]
    entry_high = signal['buy_range'][1]
    indicators = signal['indicators']
    reason = signal['analysis']
    logo_url = signal.get('logo_url', '')

    st.markdown(f""", unsafe_allow_html=True)
    <div style='border: 1px solid #ddd; border-radius: 12px; padding: 1rem; background: white; margin-bottom: 2rem; box-shadow: 0 0 6px rgba(0,0,0,0.05);'>

        <div style="padding: 6px 0 12px;">
            <div style="font-size: 13px; margin-bottom: 4px;">
                <strong style="color:#d9534f;">❌ Weak</strong> | 
                <strong style="color:#f0ad4e;">⚠️ Moderate</strong> | 
                <strong style="color:#5cb85c;">✅ Strong</strong>
            </div>
            <div style="position: relative; height: 24px; background: linear-gradient(90deg, #f8d7da 0%, #fff3cd 50%, #d4edda 100%); border-radius: 6px;">
                <div style="position: absolute; top: -8px; left: calc({buy_score}% - 10px);">
                    <span style="font-size: 11px;">⬤</span>
                    <div style="font-size: 10px; text-align: center;">{buy_score}</div>
                </div>
            </div>
        </div>

        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <img src="{logo_url}" alt="{symbol}" style="width: 40px; height: 40px; margin-right: 1rem;" onerror="this.style.display='none'"/>
            <div>
                <h4 style="margin: 0;">{name}</h4>
                <div style="font-size: 13px; color: gray;">{symbol}</div>
            </div>
        </div>

        <p style="margin-top: 1rem;"><strong>Buy Score:</strong> {buy_score}</p>
        <p><strong>Current Price:</strong> ${price:,.2f}</p>
        <p><strong>Buy Range:</strong> ${entry_low:,.2f} – ${entry_high:,.2f}</p>

        <h5 style="margin-top: 1.2rem;">📊 Subscores:</h5>
        <ul>
        {''.join([f"<li><strong>{k}:</strong> {v}</li>" for k,v in indicators.items()])}
        </ul>

        <h5 style="margin-top: 1.2rem;">🧠 Analysis:</h5>
        <p>{reason}</p>

    </div>
    """, unsafe_allow_html=True)
