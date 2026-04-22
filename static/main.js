// --- PREMIUM BOOKING STATE ---
let currentStep = 1;
let selectedPrice = 100;
let selectedTier = "Adult";
let qty = 1;
let selectedPaymentMethod = 'upi';
let payPollInterval = null;

function openBooking() {
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('visitDate');
    if (dateInput) {
        dateInput.setAttribute('min', today);
    }
    
    document.getElementById('bookingModal').style.display = 'flex';
    goStep(1);
    updateSummary();
}

function closeBooking() {
    document.getElementById('bookingModal').style.display = 'none';
}

function handleOverlayClick(e) {
    if (e.target.id === 'bookingModal') closeBooking();
}

function goStep(step) {
    if (step === 3) {
        if (selectedTier === 'Group' && qty < 5) {
            alert('Group Booking Error: You must have a minimum of 5 members to qualify for the Group Discount tier. Please add more members.');
            return;
        }
        
        if ((selectedTier === 'Group' || selectedTier === 'Student') && qty > 1) {
            const text = document.getElementById('additionalGuests').value;
            const namesCount = text.split(/[,|\n]+/).map(n => n.trim()).filter(n => n.length > 0).length;
            if (namesCount < qty - 1) {
                alert(`Security Policy: For ${selectedTier} tier bookings, you must explicitly provide the names of all ${qty - 1} additional members. Please separate each name with a comma.`);
                return;
            }
        }
    }

    // Hide all panels
    document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
    // Show target
    document.getElementById(`step${step}`).classList.add('active');
    currentStep = step;

    // Update Dots
    for (let i = 1; i <= 4; i++) {
        const dot = document.getElementById(`pd${i}`);
        if (dot) {
            if (i <= step) dot.classList.add('active');
            else dot.classList.remove('active');
        }
    }

    if (step === 3) {
        updateSummary();
        if (selectedPaymentMethod === 'upi') {
            document.getElementById('payBtn').style.display = 'none';
            if (!window.upiQRGenerated) {
                processManualPayment();
            }
        } else {
            document.getElementById('payBtn').style.display = 'inline-block';
        }
    }
}

function selectTicket(el, price, tier) {
    document.querySelectorAll('.ticket-card-mini').forEach(t => t.classList.remove('selected'));
    el.classList.add('selected');
    selectedPrice = price;
    selectedTier = tier;
    
    updateSummary();
}

function changeQty(delta) {
    qty = Math.max(1, qty + delta);
    document.getElementById('qtyVal').value = qty;
    updateSummary();
}

function manualQty() {
    let val = parseInt(document.getElementById('qtyVal').value);
    if(isNaN(val) || val < 1) val = 1;
    qty = val;
    document.getElementById('qtyVal').value = qty;
    updateSummary();
}

function onMuseumChange() {
    updateTicketPrices();
    updateSummary();
}

function updateTicketPrices() {
    const museumId = document.getElementById('museumSelect').value;
    if (!museumId) {
        if (document.getElementById('priceAdult')) document.getElementById('priceAdult').innerText = `₹---`;
        if (document.getElementById('priceStudent')) document.getElementById('priceStudent').innerText = `₹---`;
        if (document.getElementById('priceGroup')) document.getElementById('priceGroup').innerText = `₹---`;
        return;
    }


    const museum = MUSEUMS_DATA.find(m => m.id == museumId);
    if (!museum) return;

    // Update Prices in the cards
    const priceAdult = museum.price;
    const priceStudent = museum.student_price;
    const priceGroup = museum.group_price;

    document.getElementById('priceAdult').innerText = `₹${priceAdult}`;
    document.getElementById('priceStudent').innerText = `₹${priceStudent}`;
    document.getElementById('priceGroup').innerText = `₹${priceGroup}`;

    // Update onclick handlers to use NEW prices
    document.getElementById('tierAdult').setAttribute('onclick', `selectTicket(this, ${priceAdult}, 'Adult')`);
    document.getElementById('tierStudent').setAttribute('onclick', `selectTicket(this, ${priceStudent}, 'Student')`);
    document.getElementById('tierGroup').setAttribute('onclick', `selectTicket(this, ${priceGroup}, 'Group')`);

    // Force update currently selected price if tier is still the same
    if (selectedTier === "Adult") selectedPrice = priceAdult;
    else if (selectedTier === "Student") selectedPrice = priceStudent;
    else if (selectedTier === "Group") selectedPrice = priceGroup;
}

function autoUpdateQty() {
    const input = document.getElementById('additionalGuests');
    const text = input.value;
    
    // Split by commas OR newlines, trim spaces, and ignore empty strings
    const namesCount = text.split(/[,|\n]+/).map(n => n.trim()).filter(n => n.length > 0).length;
    
    // Minimum 1 ticket (for the lead visitor)
    if (namesCount > 0) {
        qty = namesCount + 1;
        document.getElementById('qtyVal').value = qty;
    } else {
        // If they delete names, safely return to 1
        qty = 1;
        document.getElementById('qtyVal').value = qty;
    }
    
    // Auto-migrate to Group Tier securely if they cross threshold
    if (qty >= 5 && selectedTier !== 'Student') {
        const groupCard = document.querySelector('.ticket-card-mini:nth-child(3)');
        if(groupCard && selectedTier !== 'Group') {
            document.querySelectorAll('.ticket-card-mini').forEach(t => t.classList.remove('selected'));
            groupCard.classList.add('selected');
            selectedPrice = 80;
            selectedTier = 'Group';
        }
    }
    
    updateSummary();
}

function updateSummary() {
    const museum = document.getElementById('museumSelect').value || "Not Selected";
    let dateStr = document.getElementById('visitDate').value || "Not Selected";
    const visitor = document.getElementById('visitorName').value || "Guest";
    const total = selectedPrice * qty;

    // Convert ISO date (e.g. 2026-04-16) to readable format (e.g. 16 Apr 2026)
    if (dateStr && /^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        try {
            const dateObj = new Date(dateStr);
            dateStr = dateObj.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
        } catch (e) {}
    }

    // Update Sidebar
    const sumMuseum = document.getElementById('sumMuseum');
    const sumDate = document.getElementById('sumDate');
    const sumQty = document.getElementById('sumQty');
    const sumTotal = document.getElementById('sumTotal');

    if(sumMuseum) sumMuseum.textContent = museum.split(',')[0];
    if(sumDate) sumDate.textContent = dateStr;
    if(sumQty) sumQty.textContent = `${qty} × ${selectedTier}`;
    if(sumTotal) sumTotal.textContent = `₹${total}`;

    // Update QR scan amount if visible
    const scanAmt = document.getElementById('qrAmount');
    if (scanAmt) scanAmt.textContent = total.toFixed(2);
}

function selectPayment(method, el) {
    document.querySelectorAll('.pay-option').forEach(m => m.classList.remove('selected'));
    el.classList.add('selected');
    selectedPaymentMethod = method;
    
    // Toggle UI
    if(method === 'upi') {
        document.getElementById('payUPI').style.display = 'block';
        document.getElementById('payCard').style.display = 'none';
        document.getElementById('payBtn').style.display = 'none';
        document.getElementById('qrAmount').textContent = (selectedPrice * qty).toFixed(2);
        if (!window.upiQRGenerated) {
            processManualPayment();
        }
    } else if(method === 'card') {
        document.getElementById('payUPI').style.display = 'none';
        document.getElementById('payCard').style.display = 'block';
        document.getElementById('payBtn').style.display = 'inline-block';
    }
}

function openPaymentModal(total, museumTitle, count, visitDate, visitorName) {
    // 1. Open Modal
    document.getElementById('bookingModal').style.display = 'flex';
    
    // 2. Pre-fill data
    const museumSelect = document.getElementById('museumSelect');
    // Try to find matching option by text
    for (let i = 0; i < museumSelect.options.length; i++) {
        if (museumSelect.options[i].text.toLowerCase().includes(museumTitle.toLowerCase())) {
            museumSelect.selectedIndex = i;
            break;
        }
    }
    
    if(visitorName) document.getElementById('visitorName').value = visitorName;
    if(visitDate) {
        const dateInput = document.getElementById('visitDate');
        // If not a strict ISO date, fallback to text so the browser doesn't reject natural language like "Tomorrow"
        if (!/^[\d]{4}-[\d]{2}-[\d]{2}$/.test(visitDate)) {
            dateInput.type = "text";
        } else {
            dateInput.type = "date";
        }
        dateInput.value = visitDate;
    }
    
    qty = count;
    document.getElementById('qtyVal').textContent = qty.toString().padStart(2, '0');
    
    // 3. Set Price/Tier logic
    if (total / count === 1) {
        selectedPrice = 1;
        selectedTier = "Student";
    } else if (total / count === 80) {
        selectedPrice = 80;
        selectedTier = "Group";
    } else {
        selectedPrice = total / count;
        selectedTier = "Adult";
    }
    
    // 4. Update UI and jump to Payment
    updateSummary();
    window.upiQRGenerated = false; // Reset generation lock
    goStep(3);
}

async function processManualPayment() {
    const museum = document.getElementById('museumSelect').value;
    const visitor = document.getElementById('visitorName').value;
    const total = selectedPrice * qty;

    if (!museum || museum === "") {
        alert("Please select a destination museum.");
        goStep(1);
        return;
    }

    const btn = document.getElementById('payBtn');
    const originalContent = btn.innerHTML;
    
    try {
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Initializing...';
        btn.disabled = true;

        // 1. Create Order on Backend
        const orderResp = await fetch('/api/create_razorpay_order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: total })
        });
        const orderData = await orderResp.json();

        if (!orderData.success) {
            if (orderData.message.includes('placeholder') || orderData.message.includes('Authentication failed')) {
                console.log("Using Mock Verification (Razorpay Credentials Missing/Invalid)");
                return demoPaymentFlow(museum, visitor, total, btn, originalContent);
            }
            throw new Error(orderData.message);
        }

        const orderId = orderData.order_id;
        console.log("Order Created:", orderId);

        if (selectedPaymentMethod === 'upi') {
            console.log("UPI Payment Selected, Generating QR...");
            // --- NEW DYNAMIC SCANNER FLOW ---
            document.getElementById('qrPlaceholder').style.display = 'flex';
            document.getElementById('dynamicQR').style.display = 'none';
            document.getElementById('payStatusLabel').textContent = "Handshaking with Server...";
            document.getElementById('qrAmount').textContent = total.toFixed(2);

            const qrResp = await fetch('/api/generate_upi_qr', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    order_id: orderId, 
                    amount: total,
                    museum: museum,
                    visitor_name: visitor
                })
            });

            console.log("QR Response Received Status:", qrResp.status);
            if (!qrResp.ok) throw new Error(`Server returned ${qrResp.status}`);
            
            const qrData = await qrResp.json();
            console.log("QR Data:", qrData);

            if (qrData.success) {
                document.getElementById('qrPlaceholder').style.display = 'none';
                document.getElementById('dynamicQR').src = qrData.qr_code;
                document.getElementById('dynamicQR').style.display = 'block';
                document.getElementById('payStatusLabel').textContent = "Scan & Pay Now";
                document.getElementById('payStatusSub').style.display = 'block';
                window.upiQRGenerated = true;
                
                // Start Polling
                startPaymentPolling(orderId, museum, visitor, total, qrData.payment_link_id);
            } else {
                throw new Error("Failed to generate QR");
            }
        } else {
            // --- STANDARD RAZORPAY MODAL FOR CARD ---
            const options = {
                "key": window.RZP_KEY_ID || "rzp_test_placeholder", 
                "amount": total * 100,
                "currency": "INR",
                "name": "MuseumBot Ticketing",
                "description": `Booking for ${museum}`,
                "order_id": orderId,
                "handler": async function (response) {
                    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying...';
                    const verifyResp = await fetch('/api/verify_razorpay_payment', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_signature: response.razorpay_signature,
                            museum: museum,
                            visitor_name: visitor,
                            visit_date: document.getElementById('visitDate').value || "Not Selected",
                            count: qty,
                            total: total
                        })
                    });
                    const verifyData = await verifyResp.json();
                    if (verifyData.success) {
                        document.getElementById('ticketNum').textContent = verifyData.ticket_no;
                        
                        let additionalNames = document.getElementById('additionalGuests').value.trim();
                        let displayName = visitor || "Valued Guest";
                        
                        if (additionalNames) {
                            displayName += `, ${additionalNames}`;
                        } else if (qty > 1) {
                            displayName += ` (+${qty-1})`;
                        }
                        
                        // Prevent UI overflow from massive lists
                        if (displayName.length > 80) displayName = displayName.substring(0, 77) + "...";
                        
                        const ticketVisitorEl = document.getElementById('ticketVisitorText');
                        if (displayName.length > 45) ticketVisitorEl.style.fontSize = "0.7rem";
                        else if (displayName.length > 25) ticketVisitorEl.style.fontSize = "0.85rem";
                        else ticketVisitorEl.style.fontSize = "1.1rem"; // default
                        
                        ticketVisitorEl.textContent = displayName;
                        document.getElementById('ticketMuseumText').textContent = museum;
                        
                        // New injected fields
                        const dateInputVal = document.getElementById('visitDate').value;
                        document.getElementById('ticketDateText').textContent = dateInputVal ? dateInputVal : "Not Selected";
                        document.getElementById('ticketPayModeText').textContent = "Card / Netbanking";
                        
                        goStep(4);
                    } else {
                        alert("Payment Verification Failed: " + verifyData.message);
                    }
                },
                "prefill": { "name": visitor, "email": "visitor@example.com" },
                "theme": { "color": "#c5a059" }
            };
            const rzp1 = new Razorpay(options);
            rzp1.open();
        }

        btn.innerHTML = originalContent;
        btn.disabled = false;

    } catch (err) {
        console.error(err);
        // Hide loading states on error
        const qrPl = document.getElementById('qrPlaceholder');
        if (qrPl) qrPl.style.display = 'none';
        const stLbl = document.getElementById('payStatusLabel');
        if (stLbl) stLbl.textContent = "Error Generating QR";
        
        alert("Payment Error: " + err.message);
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}

function startPaymentPolling(orderId, museum, visitor, total, linkId = null) {
    if (payPollInterval) clearInterval(payPollInterval);
    const maxPolls = 40; // Max 160 seconds of polling
    let pollCount = 0;
    
    payPollInterval = setInterval(async () => {
        pollCount++;
        if (pollCount > maxPolls) {
            clearInterval(payPollInterval);
            const subLabel = document.getElementById('payStatusSub');
            if (subLabel) {
                subLabel.style.display = 'block';
                subLabel.style.color = '#c5a059'; // Warning yellow
                subLabel.innerHTML = '<i class="fa-solid fa-clock"></i> Polling disconnected. Please verify payment in your UPI app or try refreshed booking.';
            }
            return;
        }

        try {
            const resp = await fetch('/api/check_payment_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    order_id: orderId,
                    payment_link_id: linkId,
                    museum: museum,
                    visitor_name: visitor,
                    visit_date: document.getElementById('visitDate').value || "Not Selected",
                    count: qty,
                    total: total
                })
            });
            const data = await resp.json();
            console.log(`DEBUG Check [${pollCount}]: Status=${data.status}, Paid=${data.paid}`);
            
            if (data.success && data.paid) {
                clearInterval(payPollInterval);
                document.getElementById('ticketNum').textContent = data.ticket_no === 'ALREADY_EXISTS' ? 'CONFIRMED' : data.ticket_no;
                
                let additionalNames = document.getElementById('additionalGuests').value.trim();
                let displayName = visitor || "Valued Guest";
                
                if (additionalNames) {
                    displayName += `, ${additionalNames}`;
                } else if (qty > 1) {
                    displayName += ` (+${qty-1})`;
                }
                
                if (displayName.length > 80) displayName = displayName.substring(0, 77) + "...";
                
                const ticketVisitorEl = document.getElementById('ticketVisitorText');
                if (displayName.length > 45) ticketVisitorEl.style.fontSize = "0.7rem";
                else if (displayName.length > 25) ticketVisitorEl.style.fontSize = "0.85rem";
                else ticketVisitorEl.style.fontSize = "1.1rem";
                
                ticketVisitorEl.textContent = displayName;
                document.getElementById('ticketMuseumText').textContent = museum;
                
                // New injected fields
                const dateInputVal = document.getElementById('visitDate').value;
                document.getElementById('ticketDateText').textContent = dateInputVal ? dateInputVal : "Not Selected";
                document.getElementById('ticketPayModeText').textContent = "UPI Transfer";
                
                goStep(4);
            } else if (data.success && (data.status === 'cancelled' || data.status === 'expired' || data.status === 'failed')) {
                console.warn("DEBUG: Terminal failure received:", data.status);
                clearInterval(payPollInterval);
                const subLabel = document.getElementById('payStatusSub');
                const mainLabel = document.getElementById('payStatusLabel');
                
                if (subLabel) {
                    subLabel.style.display = 'block';
                    subLabel.style.color = '#ff4d4d'; // Red alert
                    subLabel.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> ${data.message || 'Payment failed. Please try again.'}`;
                }
                if (mainLabel) {
                    mainLabel.textContent = "Payment Failed";
                    mainLabel.style.color = '#ff4d4d';
                }
            } else if (!data.success) {
                // If the API returns success=false (e.g. 404), maybe the session/link is invalid
                console.error("DEBUG: Backend returned error:", data.message);
                clearInterval(payPollInterval);
            }
        } catch (err) {
            console.error("Polling Error:", err);
            // Don't stop on single network error, wait for retry or timeout
        }
    }, 4000); // Poll every 4 seconds
}

async function demoPaymentFlow(museum, visitor, total, btn, originalContent) {
    // Enhanced Demo Mode to show the scanner even without real keys
    document.getElementById('qrPlaceholder').style.display = 'flex';
    document.getElementById('dynamicQR').style.display = 'none';
    document.getElementById('payStatusLabel').textContent = "Handshaking with Server...";
    document.getElementById('qrAmount').textContent = total.toFixed(2);
    
    await new Promise(r => setTimeout(r, 800));
    
    // Use a fixed demo QR or call the backend for a real one with a mock ID
    const qrResp = await fetch('/api/generate_upi_qr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            order_id: "DEMO_" + Date.now(), 
            amount: total,
            museum: museum,
            visitor_name: visitor
        })
    });

    if (!qrResp.ok) {
        const errData = await qrResp.json().catch(() => ({}));
        throw new Error(errData.message || `Server Error ${qrResp.status}`);
    }
    
    const qrData = await qrResp.json();
    
    if (qrData.success) {
        document.getElementById('qrPlaceholder').style.display = 'none';
        document.getElementById('dynamicQR').src = qrData.qr_code;
        document.getElementById('dynamicQR').style.display = 'block';
        document.getElementById('payStatusLabel').textContent = "DEMO SCANNER (Mock)";
        document.getElementById('payStatusSub').style.display = 'block';
        document.getElementById('payStatusSub').innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Awaiting Mock Payment Scan... Simulator Active';
        window.upiQRGenerated = true;
        
        // Start polling even in demo for consistency
        startPaymentPolling(null, museum, visitor, total, qrData.payment_link_id);
        
        // Finalize demo if polling isn't triggered (though it should be)
        await new Promise(r => setTimeout(r, 5000));
        
        // Note: Booking is created in startPaymentPolling for link_id success
    }
    
    btn.innerHTML = originalContent;
    btn.disabled = false;
}

async function downloadTicket() {
    const ticketDiv = document.querySelector('.e-ticket-modern');
    if (!ticketDiv) return;
    
    try {
        // Prepare ticket for clean PNG export
        ticketDiv.classList.add('download-mode');
        
        // Use html2canvas to convert the ticket component to an image
        const canvas = await html2canvas(ticketDiv, {
            scale: 2, // Enhances quality
            backgroundColor: null, // Enables transparent corners
            useCORS: true
        });
        
        // Revert ticket to UI mode
        ticketDiv.classList.remove('download-mode');
        
        // Trigger download
        const link = document.createElement('a');
        link.download = `Museum_E_Ticket_${document.getElementById('ticketNum').textContent}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    } catch (err) {
        console.error("Download Error:", err);
        alert("Failed to download the ticket. Please try again or take a screenshot.");
    }
}

// --- AI CHATBOT POLYGLOT LOGIC ---
function toggleChat() {
    const chatWidget = document.getElementById('chatWidget');
    const chatHint = document.querySelector('.chat-hint');
    
    if (chatWidget.style.display === 'none') {
        chatWidget.style.display = 'flex';
        if (chatHint) chatHint.style.display = 'none';
    } else {
        chatWidget.style.display = 'none';
        if (chatHint) chatHint.style.display = 'block';
    }
}

async function sendMessage(text) {
    const input = document.getElementById('chatInput');
    const chatBody = document.getElementById('chatBody');
    const typing = document.getElementById('chatTyping');
    const message = text || input.value.trim();

    if (!message) return;

    // Append User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.textContent = message;
    chatBody.appendChild(userDiv);
    if (!text) input.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    // Show Typing
    typing.style.display = 'block';
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        
        // Hide Typing
        typing.style.display = 'none';

        if (response.status === 401) {
            appendBotMessage("I am sorry, but you must <a href='/login' style='color:var(--primary-gold)'>log in</a> before I can process your reservation.");
            return;
        }

        appendBotMessage(data.response);
    } catch (err) {
        typing.style.display = 'none';
        appendBotMessage("I apologize, but my connection seems to have faltered. Please try again.");
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') sendMessage();
}

function quickAction(text) {
    sendMessage(text);
}


function appendBotMessage(html) {
    const chatBody = document.getElementById('chatBody');
    const botMsgContainer = document.createElement('div');
    botMsgContainer.style.display = 'flex';
    botMsgContainer.style.gap = '10px';
    botMsgContainer.style.marginBottom = '15px';
    botMsgContainer.style.alignItems = 'flex-start';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'virtual-curator-avatar';
    avatarDiv.innerHTML = `
        <svg width="35" height="35" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="18" stroke="rgba(197, 160, 89, 0.3)" stroke-width="0.5" />
            <g fill="#c5a059">
                <path d="M6 15 L20 4 L34 15 H6Z" />
                <rect x="9" y="17" width="2" height="14" rx="0.5" />
                <rect x="16" y="17" width="2" height="14" rx="0.5" />
                <rect x="22" y="17" width="2" height="14" rx="0.5" />
                <rect x="29" y="17" width="2" height="14" rx="0.5" />
                <rect x="6" y="31" width="28" height="3" rx="1" />
            </g>
        </svg>
    `;

    const botDiv = document.createElement('div');
    botDiv.className = 'message bot-message';
    botDiv.style.margin = '0';
    botDiv.innerHTML = html;

    botMsgContainer.appendChild(avatarDiv);
    botMsgContainer.appendChild(botDiv);
    chatBody.appendChild(botMsgContainer);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function handleOverlayClick(e) {
    if (e.target.id === 'bookingModal') closeBooking();
    if (e.target.id === 'discoveryOverlay') closeDiscovery();
}

// --- ARTIFACT DISCOVERY SYSTEM ---

const ARTICLE_DATA = {
    'ahmedabad': {
        title: "Science City Ahmedabad",
        tag: "Scientific Frontier",
        image: "/static/images/science_city_ahmedabad.png",
        era: "Modern Era",
        location: "Hebebat, Ahmedabad",
        text: "<p>Gujarat Science City is a premier scientific institution designed to inspire the next generation of innovators. Spread over 107 hectares, it is a hub of technological marvels and immersive learning experiences.</p><p>The center's crown jewel is the <strong>Robotics Gallery</strong>, a three-story architectural marvel featuring over 200 robots across different sectors including medicine, space, and defense. Equally stunning is the <strong>Aquatic Gallery</strong>, which houses a 28-meter long shark tunnel and diverse marine life from across the globe.</p><p>With its iconic Space Odyssey planetarium and interactive 'Hall of Science', Science City Ahmedabad stands as a testament to India's commitment to scientific progress and public engagement with technology.</p>"
    },

    // HERITAGE SITES
    'delhi': {
        title: "National Museum New Delhi",
        tag: "Premier Destination",
        image: "/static/images/national_museum_delhi.png",
        era: "Pre-historic to Modern",
        location: "Janpath, New Delhi",
        text: "<p>The National Museum in New Delhi, also known as the National Museum of India, is one of the largest museums in India. Established in 1949, it holds a variety of articles ranging from pre-historic era to modern works of art.</p><p>It functions under the Ministry of Culture, Government of India. The museum is situated on Janpath. The blueprint of the National Museum was prepared by the Maurice Gwyer Committee in May 1946. Today, it houses over 200,000 works of art, both of Indian and foreign origin, covering more than 5,000 years of cultural heritage.</p>"
    },
    'kolkata': {
        title: "Indian Museum Kolkata",
        tag: "Heritage Landmark",
        image: "/static/images/indian_museum_kolkata.png",
        era: "Established 1814",
        location: "Jawaharlal Nehru Rd, Kolkata",
        text: "<p>The Indian Museum in Central Kolkata, West Bengal, India, also referred to as the Imperial Museum at Calcutta in colonial-era texts, is the ninth oldest museum in the world, the oldest museum in India, and the largest museum in India.</p><p>It has rare collections of antiques, armor and ornaments, fossils, skeletons, mummies, and Mughal paintings. It was founded by the Asiatic Society of Bengal in Kolkata, India, in 1814. The founder curator was Nathaniel Wallich, a Danish botanist.</p>"
    },
    'hyderabad': {
        title: "Salar Jung Museum",
        tag: "Individual Collection",
        image: "/static/images/salar_jung_museum.png",
        era: "19th - 20th Century",
        location: "Darushifa, Hyderabad",
        text: "<p>The Salar Jung Museum is an art museum located at Dar-ul-Shifa, on the southern bank of the Musi River in the city of Hyderabad, Telangana, India. It is one of the three National Museums of India.</p><p>Originally a private art collection of the Salar Jung family, it was endowed to the nation after the death of Salar Jung III. It was inaugurated on 16 December 1951. It has a collection of sculptures, paintings, carvings, textiles, manuscripts, ceramics, metallic artifacts, carpets, clocks, and furniture from Japan, China, Burma, Nepal, India, Persia, Egypt, Europe, and North America.</p>"
    },
    'mumbai': {
        title: "CSMVS Mumbai",
        tag: "Saracenic Heritage",
        image: "/static/images/csmvs_mumbai.png",
        era: "Opened 1922",
        location: "Fort, Mumbai",
        text: "<p>Chhatrapati Shivaji Maharaj Vastu Sangrahalaya (CSMVS), formerly named the Prince of Wales Museum of Western India, is the main museum in Mumbai, Maharashtra. It was founded in the early years of the 20th century by prominent citizens of Mumbai, with the help of the government, to commemorate the visit of George V, who was Prince of Wales at the time.</p><p>The museum document the history of India from prehistoric times to the modern era. The museum was designed by George Wittet in the Indo-Saracenic style of architecture, incorporating elements of other styles of architecture like the Mughal, Maratha and Jain.</p>"
    },

    // ARTIFACTS
    'lion_capital': {
        title: "The Lion Capital",
        tag: "Ancient Art",
        image: "/static/images/ashoka_pillar.png",
        era: "250 BCE",
        location: "Sarnath Museum, Varanasi",
        text: "<p>The Lion Capital of Ashoka is a sculpture of four Asiatic lions standing back to back, on an elaborate base that includes other animals. A graphic representation of it was adopted as the official Emblem of India in 1950.</p><p>The capital is carved out of a single block of polished sandstone, and was always a separate piece from the column itself. It features the Ashoka Chakra (Wheel of Dharma) which is also found on the National Flag of India.</p>",
        isArtifact: true
    },
    'dancing_girl': {
        title: "The Dancing Girl",
        tag: "Indus Valley",
        image: "/static/images/dancing_girl.png",
        era: "2300–1750 BCE",
        location: "Mohenjo-daro",
        text: "<p>Dancing Girl is a prehistoric bronze sculpture made in lost-wax casting about 2300–1750 BCE in the Indus Valley Civilisation city of Mohenjo-daro, which was one of the earliest cities in the world.</p><p>The statue is 10.5 centimetres (4.1 in) tall, and depicts a young woman or girl with quite long legs and arms, standing in a confident, naturalistic pose. It is a masterpiece that reveals the advanced level of Harappan metallurgical skill.</p>",
        isArtifact: true
    },
    'relics': {
        title: "Civilization Relics",
        tag: "Archaeology",
        image: "/static/images/harappan_gallery.png",
        era: "Bronze Age",
        location: "Harappan Sites",
        text: "<p>Indus Valley Civilization seals are some of the most famous artifacts from the era. These small, flat, square or rectangular objects were typically made of steatite (a soft stone) and featured intricate carvings of animals, plants, and a mysterious script that remains undeciphered.</p><p>The seals were used primarily for trade and administration, serving as a form of identification or signature for goods. Each seal was unique and reflected the identity and status of its owner.</p>",
        isArtifact: true
    },
    'manuscripts': {
        title: "Ancient Manuscripts",
        tag: "Sacred Texts",
        image: "/static/images/manuscript_gallery.png",
        era: "Medieval Period",
        location: "National Archives",
        text: "<p>Indian manuscripts were traditionally written on organic materials like palm leaf (tala-patra) or birch bark (bhurja-patra). These materials were meticulously prepared to ensure longevity and were often bound together using wooden covers.</p><p>They cover a vast range of subjects, from religious and philosophical texts like the Vedas and Upanishads to scientific treatises on astronomy, medicine (Ayurveda), and mathematics, preserving the intellectual legacy of ancient India.</p>",
        isArtifact: true
    },
    'armoury': {
        title: "Imperial Armoury",
        tag: "Military History",
        image: "/static/images/arms_gallery.png",
        era: "Mughal & Maratha",
        location: "Regional Museums",
        text: "<p>The Imperial Armoury collections showcase the exceptional craftsmanship of Indian weaponsmiths. From the legendary Damascus steel blades (Wootz) to ornate shields inlaid with precious metals, these weapons were symbols of power and prestige.</p><p>The collection includes the Talwar (curved sword), the Katar (punch dagger), and various types of matchlock muskets, reflecting the evolution of warfare and metalwork during the Mughal and Maratha eras.</p>",
        isArtifact: true
    },
    'tanjore': {
        title: "Tanjore Art",
        tag: "Devotional Art",
        image: "/static/images/tanjore_painting.png",
        era: "16th - 18th Century",
        location: "Thanjavur, Tamil Nadu",
        text: "<p>Thanjavur painting is a classical South Indian painting style, which was inaugurated from the town of Thanjavur (anglicized as Tanjore). The art form draws its immediate resources and inspiration from way back about 1600 AD.</p><p>These paintings are characterized by rich, flat and vivid colors, simple iconic composition, glittering gold foils overlaid on delicate but extensive gesso work and inlays of glass beads and pieces or very rarely precious and semi-precious gems.</p>",
        isArtifact: true
    }
};

function discoverItem(id) {
    const data = ARTICLE_DATA[id];
    if (!data) return;

    const content = `
        <div class="article-hero">
            <img src="${data.image}" alt="${data.title}">
            <div class="article-hero-overlay">
                <div>
                    <span class="article-tag">${data.tag}</span>
                    <h2>${data.title}</h2>
                </div>
            </div>
        </div>
        <div class="article-body">
            <div class="article-text">
                ${data.text}
                <div style="margin-top: 40px;">
                    ${data.isArtifact ? '' : `<button class="cta-btn" onclick="closeDiscovery(); openBooking();">Book Tickets to Visit</button>`}
                    <button class="cta-btn secondary" onclick="closeDiscovery()" style="${data.isArtifact ? '' : 'margin-left: 15px;'}">Close Reading</button>
                </div>
            </div>
            <div class="article-sidebar">
                <span class="sidebar-title">Artifact Details</span>
                <div class="sidebar-info-row">
                    <span>Era/Period</span>
                    <span style="color:var(--primary-gold)">${data.era}</span>
                </div>
                <div class="sidebar-info-row">
                    <span>Current Exhibit</span>
                    <span style="color:var(--primary-gold)">${data.title.split(' ')[0]} Gallery</span>
                </div>
                <div class="sidebar-info-row" style="border:none;">
                    <span>Location</span>
                    <span style="color:var(--primary-gold)">${data.location}</span>
                </div>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid var(--border-gold); font-size: 0.8rem; color: var(--text-muted); font-style: italic;">
                    Explore more through our AI Virtual Curator. Launch the chatbot for a guided discussion.
                </div>
            </div>
        </div>
    `;

    document.getElementById('discoveryContent').innerHTML = content;
    document.getElementById('discoveryOverlay').style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Disable scroll
}

function closeDiscovery() {
    document.getElementById('discoveryOverlay').style.display = 'none';
    document.body.style.overflow = 'auto'; // Re-enable scroll
}

// Global reveal on scroll logic
const revealObs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1 });


document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));
});

let lastScrollTop = 0;
window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    // Smart Sticky Header: Hide on scroll down, show on scroll up
    if (scrollTop > lastScrollTop && scrollTop > 150) {
        nav.classList.add('nav-hidden');
    } else {
        nav.classList.remove('nav-hidden');
    }
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;

    // Navbar Scroll Logic
    const announcement = document.querySelector('.top-announcement');
    const isAnnouncementVisible = announcement && !announcement.classList.contains('hidden');

    if (window.scrollY > 50) {
        nav.classList.add('nav-scrolled');
        if (isAnnouncementVisible) {
            nav.style.top = '0'; // Move nav to top when scrolling even if announcement is there
        }
    } else {
        nav.classList.remove('nav-scrolled');
        if (isAnnouncementVisible) {
            nav.style.top = '35px'; // Back to below announcement
        } else {
            nav.style.top = '0';
        }
    }
});

// Auto-hide announcement bar after 50 seconds
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const announcement = document.querySelector('.top-announcement');
        const nav = document.getElementById('navbar');
        if (announcement) {
            announcement.classList.add('hidden');
            // Move navbar to top permanently
            if (nav) {
                nav.style.top = '0';
            }
        }
    }, 50000); // 50 seconds
});
// Reveal Animation Observer
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
        }
    });
}, {
    threshold: 0.15
});

window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.reveal').forEach(el => {
        revealObserver.observe(el);
    });
});
