import React, { Component } from 'react';

class ReportDetail extends Component {
    handleAction = (action) => {
        const { reportId } = this.props; // Assuming you have the report ID available

        fetch(`/api/v1/reports/${reportId}/`, {
            method: 'PUT', // You can also use 'POST' depending on your API
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action }),
        })
        .then(response => response.json())
        .then(data => {
            // Handle the response data if needed
        })
        .catch(error => {
            // Handle errors
        });
    };

    render() {
        return (
            <div>
                {/* Your report details */}
                <button onClick={() => this.handleAction('save_for_later')}>Save for Later</button>
                <button onClick={() => this.handleAction('preview')}>Preview</button>
                <button onClick={() => this.handleAction('publish')}>Publish</button>
            </div>
        );
    }
}

export default ReportDetail;
