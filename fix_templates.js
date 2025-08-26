// Helper script to fix complex template literals
function showIPDetails(ipAddress) {
    const ipInfo = currentIPData.find(ip => ip.ip === ipAddress);
    if (!ipInfo) return;
    
    let detailsHTML = '<div style="padding: 20px;">' +
        '<h3 style="color: #ef4444; margin-bottom: 20px;">Detailed Information for ' + ipAddress + '</h3>' +
        '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">' +
            '<div>' +
                '<strong style="color: #60a5fa;">Status:</strong> ' +
                '<span style="color: #f59e0b;">' + ipInfo.status + '</span>' +
            '</div>' +
            '<div>' +
                '<strong style="color: #60a5fa;">Lock Type:</strong> ' +
                '<span style="color: #f59e0b;">' + (ipInfo.lockout_type || 'Unknown') + '</span>' +
            '</div>' +
            '<div>' +
                '<strong style="color: #60a5fa;">Reference Code:</strong> ' +
                '<span style="color: white; font-family: monospace;">' + (ipInfo.reference_code || 'N/A') + '</span>' +
            '</div>' +
            '<div>' +
                '<strong style="color: #60a5fa;">Total Attempts:</strong> ' +
                '<span style="color: #ef4444; font-weight: bold;">' + (ipInfo.total_attempts || 0) + '</span>' +
            '</div>' +
            '<div>' +
                '<strong style="color: #60a5fa;">First Seen:</strong> ' +
                '<span style="color: #94a3b8;">' + (ipInfo.first_seen || 'Unknown') + '</span>' +
            '</div>' +
            '<div>' +
                '<strong style="color: #60a5fa;">Locked At:</strong> ' +
                '<span style="color: #94a3b8;">' + (ipInfo.locked_at || 'Unknown') + '</span>' +
            '</div>' +
        '</div>' +
        '<div style="margin-bottom: 20px;">' +
            '<strong style="color: #60a5fa;">User Agent:</strong>' +
            '<div style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 5px;">' +
                (ipInfo.user_agent || 'Unknown') +
            '</div>' +
        '</div>' +
        '<div style="margin-bottom: 20px;">' +
            '<strong style="color: #60a5fa;">Failed Passwords:</strong>' +
            '<div style="margin-top: 10px;">';
    
    // Handle failed passwords
    if (ipInfo.failed_passwords && ipInfo.failed_passwords.length > 0) {
        for (let i = 0; i < ipInfo.failed_passwords.length; i++) {
            detailsHTML += '<span style="display: inline-block; background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 5px 10px; margin: 5px; border-radius: 5px; font-family: monospace;">' + 
                ipInfo.failed_passwords[i] + '</span>';
        }
    } else {
        detailsHTML += '<span style="color: #94a3b8;">No passwords logged</span>';
    }
    
    detailsHTML += '</div></div>';
    
    // Handle attempt history
    if (ipInfo.attempt_history && ipInfo.attempt_history.length > 0) {
        detailsHTML += '<div style="margin-bottom: 20px;">' +
            '<strong style="color: #60a5fa;">Recent Attempt History:</strong>' +
            '<div style="margin-top: 10px; max-height: 200px; overflow-y: auto;">';
        
        for (let i = 0; i < ipInfo.attempt_history.length; i++) {
            const attempt = ipInfo.attempt_history[i];
            detailsHTML += '<div style="padding: 10px; margin: 5px 0; background: rgba(0,0,0,0.3); border-radius: 5px; border-left: 3px solid #ef4444;">' +
                '<div style="color: #ef4444; font-family: monospace;">' + attempt.password + '</div>' +
                '<div style="color: #94a3b8; font-size: 0.85rem; margin-top: 5px;">' +
                    new Date(attempt.timestamp).toLocaleString('en-GB') + ' | Type: ' + attempt.type +
                '</div>' +
            '</div>';
        }
        
        detailsHTML += '</div></div>';
    }
    
    detailsHTML += '<div style="margin-top: 20px; text-align: right;">' +
        '<button onclick="closeIPDetails()" style="background: #475569; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">' +
            'Close' +
        '</button>' +
    '</div></div>';
    
    // Rest of function...
}