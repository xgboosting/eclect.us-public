export function makeCard(filing) {
    const priceChange5 = (filing.price_change_5_days * 100).toFixed(2);
    const priceChange10 = (filing.price_change_10_days * 100).toFixed(2);
    const priceChange20 = (filing.price_change_20_days * 100).toFixed(2);
    const priceChange40 = (filing.price_change_40_days * 100).toFixed(2);
    return `
    <div class="card pt-3 pb-3 mb-5">
        <div class="flex-wrap">
        <div class="filing">
            <div class="row">
                <div class="col">
                    <span class="short-name">
                        <a href="/#search/${filing.symbol}">${filing.symbol}</a>
                    </span>
                    <span class="long-name">
                        ${filing.shortname}
                    </span>
                </div>
                ${
                    filing.price_change_5_days ? `
                        <div class="col text-right">
                            <span class="${priceChange5 >= 0 ? 'positive-change' : 'negative-change'}">
                                ${
                                    priceChange5 >= 0 ? `+${priceChange5}` : priceChange5
                                }%
                            </span>
                            <span class="change-hint">
                                5 days after published
                            </span>
                        </div>
                    ` : '<div class="col text-right"></div>'
                }
                ${
                    filing.price_change_10_days ? `
                        <div class="col text-right">
                            <span class="${priceChange10 >= 0 ? 'positive-change' : 'negative-change'}">
                                ${
                                    priceChange10 >= 0 ? `+${priceChange10}` : priceChange10
                                }%
                            </span>
                            <span class="change-hint">
                                10 days after published
                            </span>
                        </div>
                    ` : '<div class="col text-right"></div>'
                }
                ${
                    filing.price_change_20_days ? `
                        <div class="col text-right">
                            <span class="${priceChange20 >= 0 ? 'positive-change' : 'negative-change'}">
                                ${
                                    priceChange20 >= 0 ? `+${priceChange20}` : priceChange20
                                }%
                            </span>
                            <span class="change-hint">
                                20 days after published
                            </span>
                        </div>
                    ` : '<div class="col text-right"></div>'
                }
                ${
                    filing.price_change_40_days ? `
                        <div class="col text-right">
                            <span class="${priceChange40 >= 0 ? 'positive-change' : 'negative-change'}">
                                ${
                                    priceChange40 >= 0 ? `+${priceChange40}` : priceChange40
                                }%
                            </span>
                            <span class="change-hint">
                                40 days after published
                            </span>
                        </div>
                    ` : '<div class="col text-right"></div>'
                }
            </div>

            <table>
                <tbody>
                    <tr>
                        <td class="font-weight-bold">
                            Country
                        </td>
                        <td>
                            ${filing.country}
                        </td>
                    </tr>
                    <tr>
                        <td class="font-weight-bold">
                            Industry
                        </td>
                        <td>
                            ${filing.industry}
                        </td>
                    </tr>
                    <tr>
                        <td class="font-weight-bold">
                            Market cap
                        </td>
                        <td>
                            ${filing.marketcap}
                        </td>
                    </tr>
                    <tr>
                        <td class="font-weight-bold">
                            Date
                        </td>
                        <td>
                            ${filing.date}
                        </td>
                    </tr>
                    <tr>
                        <td class="font-weight-bold">
                            Report type
                        </td>
                        <td>
                            ${filing.file_type.toUpperCase()}
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="links">
                <a href="${filing.original_filing_link}"
                    rel="noreferrer noopener" target="_blank">
                    View original filing
                </a>
                <a href="${filing.financials_link}"
                    rel="noreferrer noopener" target="_blank">
                    View financials
                </a>
            </div>

            <span class="highlights-title">
               Risk Factors 
            </span>
            <ul class="highlights">
                ${
                    [...filing.rf_highlights].map(highlight => `
                        <li>
                            ${highlight.sentence}
                        </li>
                    `).join('\n')
                }
            </ul>
            <span class="highlights-title">
                Discussion and analysis
            </span>

            <ul class="highlights">
                ${
                    [...filing.daa_highlights].map(highlight => `
                        <li>
                            ${highlight.sentence}
                        </li>
                    `).join('\n')
                }
            </ul>
        </div>
        </div>
    </div>
    `
}