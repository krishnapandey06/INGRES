// ==================================================
// INGRES WEB DASHBOARD
// Frontend JavaScript
// ==================================================


// ==================================================
// CONFIGURATION
// ==================================================

const API_URL = "http://127.0.0.1:8000";

const DISTRICT_GEOJSON_URL =
    "https://raw.githubusercontent.com/ishawakankar/India_Districts/master/india_district.geojson";


// ==================================================
// GROUNDWATER CATEGORY COLORS
// ==================================================

const GROUNDWATER_COLORS = {

    "Safe":
        "#22c55e",

    "Semi-Critical":
        "#eab308",

    "Critical":
        "#f97316",

    "Over-Exploited":
        "#ef4444",

    "Unknown":
        "#9ca3af"

};


// ==================================================
// GLOBAL MAP VARIABLES
// ==================================================

let indiaMap = null;

let districtLayer = null;

let selectedMapLayer = null;

let districtGeoJSON = null;

let groundwaterData = [];

let groundwaterLookup = {};


// ==================================================
// DATASET VARIABLES
// ==================================================

let datasetRecords = [];

let datasetColumns = [];

let datasetCurrentPage = 1;

const DATASET_PAGE_SIZE = 25;

let datasetLoaded = false;


// ==================================================
// TAB MANAGEMENT
// ==================================================

function showTab(
    tabId,
    buttonElement
) {

    const tabs =
        document.querySelectorAll(
            ".tab-content"
        );


    tabs.forEach(
        function(tab) {

            tab.classList.remove(
                "active"
            );

        }
    );


    const buttons =
        document.querySelectorAll(
            ".nav-button"
        );


    buttons.forEach(
        function(button) {

            button.classList.remove(
                "active"
            );

        }
    );


    const selectedTab =
        document.getElementById(
            tabId
        );


    if (selectedTab) {

        selectedTab.classList.add(
            "active"
        );

    }


    if (buttonElement) {

        buttonElement.classList.add(
            "active"
        );

    }


    // ----------------------------------------------
    // MAP TAB
    // ----------------------------------------------

    if (
        tabId === "map"
        &&
        indiaMap
    ) {

        setTimeout(
            function() {

                indiaMap.invalidateSize();

            },
            100
        );

    }


    // ----------------------------------------------
    // DATASET TAB
    // ----------------------------------------------

    if (
        tabId === "dataset"
    ) {

        initializeDatasetTab();

    }

}


// ==================================================
// NORMALIZE LOCATION NAME
// ==================================================

function normalizeLocationName(
    value
) {

    if (!value) {

        return "";

    }


    return String(value)
        .toLowerCase()
        .trim()
        .replace(
            /&/g,
            "and"
        )
        .replace(
            /[^a-z0-9]/g,
            ""
        );

}


// ==================================================
// NORMALIZE CATEGORY
// ==================================================

function normalizeCategory(
    value
) {

    if (!value) {

        return "Unknown";

    }


    const category =
        String(value)
            .trim()
            .toLowerCase();


    if (
        category === "safe"
    ) {

        return "Safe";

    }


    if (
        category === "semi-critical"
        ||
        category === "semi critical"
        ||
        category === "semicritical"
    ) {

        return "Semi-Critical";

    }


    if (
        category === "critical"
    ) {

        return "Critical";

    }


    if (
        category === "over-exploited"
        ||
        category === "over exploited"
        ||
        category === "overexploited"
    ) {

        return "Over-Exploited";

    }


    return "Unknown";

}


// ==================================================
// LOCATION MATCHING
// ==================================================

function locationNamesMatch(
    value1,
    value2
) {

    if (
        !value1 ||
        !value2
    ) {

        return false;

    }


    if (
        value1 === value2
    ) {

        return true;

    }


    const aliases = {

        "bangalorerural":
            "bengalururural",

        "bangaloreurban":
            "bengaluruurban",

        "tamilnad":
            "tamilnadu",

        "orissa":
            "odisha",

        "uttaranchal":
            "uttarakhand",

        "pondicherry":
            "puducherry"

    };


    const normalized1 =
        aliases[value1] ||
        value1;


    const normalized2 =
        aliases[value2] ||
        value2;


    return (
        normalized1 ===
        normalized2
    );

}


// ==================================================
// GET DISTRICT NAME
// ==================================================

function getDistrictName(
    properties
) {

    const possibleNames = [

        "DISTRICT",
        "District",
        "district",
        "NAME_2",
        "NAME_3",
        "dtname",
        "DTNAME",
        "DT_NAME",
        "DISTRICT_NAME",
        "district_name",
        "name"

    ];


    for (
        const key of possibleNames
    ) {

        if (
            properties[key]
        ) {

            return String(
                properties[key]
            );

        }

    }


    return "";

}


// ==================================================
// GET STATE NAME
// ==================================================

function getStateName(
    properties
) {

    const possibleNames = [

        "STATE",
        "State",
        "state",
        "ST_NM",
        "STNAME",
        "NAME_1",
        "stname",
        "state_name"

    ];


    for (
        const key of possibleNames
    ) {

        if (
            properties[key]
        ) {

            return String(
                properties[key]
            );

        }

    }


    return "";

}


// ==================================================
// LOAD GROUNDWATER MAP DATA
// ==================================================

async function loadGroundwaterData() {

    try {

        console.log(
            "Loading groundwater map data..."
        );


        const response =
            await fetch(
                `${API_URL}/api/map-data`
            );


        if (!response.ok) {

            throw new Error(
                `Map API failed: ${response.status}`
            );

        }


        const result =
            await response.json();


        if (!result.success) {

            throw new Error(
                result.error ||
                "Could not load groundwater data."
            );

        }


        groundwaterData =
            result.data || [];


        console.log(
            "Groundwater records loaded:",
            groundwaterData.length
        );


        createGroundwaterLookup();

    }

    catch (error) {

        console.error(
            "Groundwater data loading error:",
            error
        );


        groundwaterData = [];

    }

}


// ==================================================
// CREATE GROUNDWATER LOOKUP
// ==================================================

function createGroundwaterLookup() {

    groundwaterLookup = {};


    groundwaterData.forEach(
        function(record) {

            const state =
                normalizeLocationName(
                    record.state
                );


            const district =
                normalizeLocationName(
                    record.district
                );


            const key =
                `${state}|${district}`;


            groundwaterLookup[key] =
                record;

        }
    );


}


// ==================================================
// FIND GROUNDWATER RECORD
// ==================================================

function findGroundwaterRecord(
    properties
) {

    if (!properties) {

        return null;

    }


    const state =
        normalizeLocationName(
            getStateName(
                properties
            )
        );


    const district =
        normalizeLocationName(
            getDistrictName(
                properties
            )
        );


    if (!district) {

        return null;

    }


    const key =
        `${state}|${district}`;


    if (
        groundwaterLookup[key]
    ) {

        return groundwaterLookup[key];

    }


    const matches =
        groundwaterData.filter(
            function(record) {

                return locationNamesMatch(

                    normalizeLocationName(
                        record.district
                    ),

                    district

                );

            }
        );


    if (
        matches.length === 1
    ) {

        return matches[0];

    }


    return null;

}


// ==================================================
// GET CATEGORY COLOR
// ==================================================

function getCategoryColor(
    category
) {

    const normalized =
        normalizeCategory(
            category
        );


    return (
        GROUNDWATER_COLORS[
            normalized
        ]
        ||
        GROUNDWATER_COLORS[
            "Unknown"
        ]
    );

}


// ==================================================
// DEFAULT MAP STYLE
// ==================================================

function defaultDistrictStyle(
    feature
) {

    const record =
        findGroundwaterRecord(
            feature.properties
        );


    if (!record) {

        return {

            color:
                "#ffffff",

            weight:
                0.8,

            fillColor:
                GROUNDWATER_COLORS[
                    "Unknown"
                ],

            fillOpacity:
                0.55

        };

    }


    const category =
        normalizeCategory(
            record.category
        );


    return {

        color:
            "#ffffff",

        weight:
            0.8,

        fillColor:
            getCategoryColor(
                category
            ),

        fillOpacity:
            0.72

    };

}


// ==================================================
// POPUP CONTENT
// ==================================================

function createGroundwaterPopup(
    districtName,
    stateName,
    record
) {

    if (!record) {

        return `

            <div>

                <strong>
                    ${escapeHtml(
                        districtName ||
                        "District"
                    )}
                </strong>

                <br>

                ${escapeHtml(
                    stateName ||
                    "India"
                )}

                <br><br>

                Groundwater data unavailable.

            </div>

        `;

    }


    const category =
        normalizeCategory(
            record.category
        );


    let extraction =
        "N/A";


    if (
        record.extraction !== null
        &&
        record.extraction !== undefined
        &&
        record.extraction !== ""
    ) {

        extraction =
            `${Number(
                record.extraction
            ).toFixed(2)}%`;

    }


    const categoryColor =
        getCategoryColor(
            category
        );


    return `

        <div style="
            min-width:210px;
            font-family:Arial,sans-serif;
        ">

            <div style="
                font-size:17px;
                font-weight:bold;
                margin-bottom:7px;
            ">

                ${escapeHtml(
                    districtName ||
                    "District"
                )}

            </div>


            <div style="
                margin-bottom:6px;
                color:#555;
            ">

                <strong>
                    State:
                </strong>

                ${escapeHtml(
                    stateName ||
                    "India"
                )}

            </div>


            <div style="
                margin-bottom:6px;
            ">

                <strong>
                    Groundwater Extraction:
                </strong>

                ${extraction}

            </div>


            <div>

                <strong>
                    Status:
                </strong>

                <span style="
                    display:inline-block;
                    margin-left:5px;
                    padding:4px 8px;
                    border-radius:5px;
                    background:${categoryColor};
                    color:white;
                    font-weight:bold;
                    font-size:12px;
                ">

                    ${category}

                </span>

            </div>

        </div>

    `;

}


// ==================================================
// DISTRICT EVENTS
// ==================================================

function setupDistrictFeature(
    feature,
    layer
) {

    const properties =
        feature.properties || {};


    const districtName =
        getDistrictName(
            properties
        );


    const stateName =
        getStateName(
            properties
        );


    const record =
        findGroundwaterRecord(
            properties
        );


    layer.bindPopup(

        createGroundwaterPopup(

            districtName,

            stateName,

            record

        )

    );


    layer.on({

        mouseover:
            function() {

                if (
                    selectedMapLayer !==
                    layer
                ) {

                    layer.setStyle({

                        weight:
                            2,

                        color:
                            "#1769aa",

                        fillOpacity:
                            0.88

                    });

                }

            },


        mouseout:
            function() {

                if (
                    selectedMapLayer !==
                    layer
                ) {

                    districtLayer.resetStyle(
                        layer
                    );

                }

            },


        click:
            function() {

                if (
                    selectedMapLayer
                    &&
                    selectedMapLayer !==
                    layer
                ) {

                    districtLayer.resetStyle(
                        selectedMapLayer
                    );

                }


                selectedMapLayer =
                    layer;


                layer.setStyle({

                    weight:
                        3,

                    color:
                        "#1769aa",

                    fillColor:
                        "#3b82f6",

                    fillOpacity:
                        0.9

                });


                layer.bringToFront();

            }

    });

}


// ==================================================
// INITIALIZE INDIA MAP
// ==================================================

async function initializeIndiaMap() {

    const mapContainer =
        document.getElementById(
            "india-map"
        );


    if (!mapContainer) {

        return;

    }


    if (indiaMap) {

        return;

    }


    indiaMap =
        L.map(
            "india-map",
            {

                center: [
                    22.5,
                    79.0
                ],

                zoom:
                    4.6,

                minZoom:
                    4,

                maxZoom:
                    9,

                zoomControl:
                    true

            }
        );


    L.tileLayer(

        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

        {

            maxZoom:
                19,

            attribution:
                "&copy; OpenStreetMap contributors"

        }

    ).addTo(
        indiaMap
    );


    await loadGroundwaterData();

    await loadDistrictGeoJSON();

    createMapLegend();

}


// ==================================================
// LOAD DISTRICT GEOJSON
// ==================================================

async function loadDistrictGeoJSON() {

    const selection =
        document.getElementById(
            "map-selection"
        );


    try {

        if (selection) {

            selection.textContent =
                "Loading India district boundaries...";

        }


        const response =
            await fetch(
                DISTRICT_GEOJSON_URL
            );


        if (!response.ok) {

            throw new Error(
                "Could not load district GeoJSON."
            );

        }


        districtGeoJSON =
            await response.json();


        districtLayer =
            L.geoJSON(

                districtGeoJSON,

                {

                    style:
                        defaultDistrictStyle,

                    onEachFeature:
                        setupDistrictFeature

                }

            ).addTo(
                indiaMap
            );


        indiaMap.fitBounds(

            districtLayer.getBounds(),

            {

                padding: [
                    20,
                    20
                ]

            }

        );


        if (selection) {

            selection.textContent =
                "India map loaded. Search a state or district.";

        }


    }

    catch (error) {

        console.error(
            "Map loading error:",
            error
        );


        if (selection) {

            selection.textContent =
                "Could not load district boundaries.";

        }

    }

}


// ==================================================
// MAP LEGEND
// ==================================================

function createMapLegend() {

    if (!indiaMap) {

        return;

    }


    const legend =
        L.control({

            position:
                "bottomright"

        });


    legend.onAdd =
        function() {

            const div =
                L.DomUtil.create(
                    "div",
                    "groundwater-legend"
                );


            div.style.background =
                "white";

            div.style.padding =
                "12px 14px";

            div.style.borderRadius =
                "8px";

            div.style.boxShadow =
                "0 2px 8px rgba(0,0,0,0.25)";

            div.style.fontFamily =
                "Arial, sans-serif";

            div.style.fontSize =
                "13px";

            div.style.lineHeight =
                "20px";


            div.innerHTML = `

                <div style="
                    font-weight:bold;
                    margin-bottom:7px;
                    font-size:14px;
                ">

                    Groundwater Status

                </div>


                <div>
                    🟢 Safe
                </div>

                <div>
                    🟡 Semi-Critical
                </div>

                <div>
                    🟠 Critical
                </div>

                <div>
                    🔴 Over-Exploited
                </div>

                <div>
                    ⚪ Unknown
                </div>

            `;


            return div;

        };


    legend.addTo(
        indiaMap
    );

}


// ==================================================
// SELECT DISTRICT
// ==================================================

function selectDistrict(
    districtName,
    stateName
) {

    if (!districtLayer) {

        return false;

    }


    const normalizedDistrict =
        normalizeLocationName(
            districtName
        );


    const normalizedState =
        normalizeLocationName(
            stateName
        );


    let foundLayer =
        null;


    districtLayer.eachLayer(
        function(layer) {

            const properties =
                layer.feature.properties ||
                {};


            const layerDistrict =
                normalizeLocationName(
                    getDistrictName(
                        properties
                    )
                );


            const layerState =
                normalizeLocationName(
                    getStateName(
                        properties
                    )
                );


            const districtMatches =
                locationNamesMatch(

                    layerDistrict,

                    normalizedDistrict

                );


            const stateMatches =
                !normalizedState
                ||
                locationNamesMatch(

                    layerState,

                    normalizedState

                );


            if (
                districtMatches
                &&
                stateMatches
            ) {

                foundLayer =
                    layer;

            }

        }
    );


    if (!foundLayer) {

        return false;

    }


    if (
        selectedMapLayer
        &&
        selectedMapLayer !==
        foundLayer
    ) {

        districtLayer.resetStyle(
            selectedMapLayer
        );

    }


    selectedMapLayer =
        foundLayer;


    foundLayer.setStyle({

        weight:
            3,

        color:
            "#1769aa",

        fillColor:
            "#3b82f6",

        fillOpacity:
            0.9

    });


    foundLayer.bringToFront();


    indiaMap.fitBounds(

        foundLayer.getBounds(),

        {

            padding: [
                40,
                40
            ],

            maxZoom:
                8

        }

    );


    foundLayer.openPopup();


    const selection =
        document.getElementById(
            "map-selection"
        );


    if (selection) {

        selection.textContent =
            `${districtName}, ${stateName} selected.`;

    }


    return true;

}


// ==================================================
// SELECT STATE
// ==================================================

function selectState(
    stateName
) {

    if (!districtLayer) {

        return false;

    }


    const normalizedState =
        normalizeLocationName(
            stateName
        );


    let matchingLayers =
        [];


    districtLayer.eachLayer(
        function(layer) {

            const properties =
                layer.feature.properties ||
                {};


            const layerState =
                normalizeLocationName(
                    getStateName(
                        properties
                    )
                );


            if (
                locationNamesMatch(

                    layerState,

                    normalizedState

                )
            ) {

                matchingLayers.push(
                    layer
                );

            }

        }
    );


    if (
        matchingLayers.length === 0
    ) {

        return false;

    }


    if (
        selectedMapLayer
    ) {

        districtLayer.resetStyle(
            selectedMapLayer
        );

        selectedMapLayer =
            null;

    }


    matchingLayers.forEach(
        function(layer) {

            layer.setStyle({

                weight:
                    1.5,

                color:
                    "#1769aa",

                fillOpacity:
                    0.82

            });

        }
    );


    const group =
        L.featureGroup(
            matchingLayers
        );


    indiaMap.fitBounds(

        group.getBounds(),

        {

            padding: [
                30,
                30
            ],

            maxZoom:
                7

        }

    );


    const selection =
        document.getElementById(
            "map-selection"
        );


    if (selection) {

        selection.textContent =
            `${stateName} selected.`;

    }


    return true;

}


// ==================================================
// UPDATE MAP FROM CHAT RESPONSE
// ==================================================

function updateMapFromResponse(
    data
) {

    if (!data) {

        return;

    }


    let state =
        data.state ||
        "";

    let district =
        data.district ||
        "";


    const structured =
        data.complete_structured_result ||
        {};


    if (
        !state &&
        structured.STATE
    ) {

        const stateValues =
            Object.values(
                structured.STATE
            );

        if (stateValues.length > 0) {
            state = stateValues[0];
        }

    }


    if (
        !district &&
        structured.DISTRICT
    ) {

        const districtValues =
            Object.values(
                structured.DISTRICT
            );

        if (districtValues.length > 0) {
            district = districtValues[0];
        }

    }


    const analysis =
        data.analysis ||
        {};


    if (
        !state &&
        Array.isArray(analysis.states) &&
        analysis.states.length > 0
    ) {

        state = analysis.states[0];

    }


    if (
        !district &&
        Array.isArray(analysis.districts) &&
        analysis.districts.length > 0
    ) {

        district = analysis.districts[0];

    }


    console.log(
        "INGRES map location:",
        { district: district, state: state }
    );


    if (district && state) {

        const found =
            selectDistrict(
                district,
                state
            );

        if (found) {
            return;
        }

    }


    if (district) {

        const found =
            selectDistrict(
                district,
                ""
            );

        if (found) {
            return;
        }

    }


    if (state) {

        selectState(state);

    }

}


// ==================================================
// ENTER KEY
// ==================================================

function handleEnter(
    event
) {

    if (
        event.key === "Enter"
    ) {

        event.preventDefault();

        sendQuery();

    }

}


// ==================================================
// ADD USER MESSAGE
// ==================================================

function addUserMessage(
    query
) {

    const messages =
        document.getElementById(
            "chat-messages"
        );


    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message user";


    message.innerHTML = `

        <div class="message-content">

            <strong>
                You
            </strong>

            <p>
                ${escapeHtml(query)}
            </p>

        </div>

        <div class="message-avatar">
            U
        </div>

    `;


    messages.appendChild(
        message
    );


    scrollChatToBottom();

}


// ==================================================
// ADD INGRES MESSAGE
// ==================================================

function addAssistantMessage(
    response
) {

    const messages =
        document.getElementById(
            "chat-messages"
        );


    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message assistant";


    const formattedResponse =
        escapeHtml(
            response
        )
        .replace(
            /\n/g,
            "<br>"
        );


    message.innerHTML = `

        <div class="message-avatar">
            I
        </div>

        <div class="message-content">

            <strong>
                INGRES
            </strong>

            <p>
                ${formattedResponse}
            </p>

        </div>

    `;


    messages.appendChild(
        message
    );


    scrollChatToBottom();

}


// ==================================================
// LOADING MESSAGE
// ==================================================

function addLoadingMessage() {

    const messages =
        document.getElementById(
            "chat-messages"
        );


    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message assistant";


    message.id =
        "loading-message";


    message.innerHTML = `

        <div class="message-avatar">
            I
        </div>

        <div class="message-content">

            <strong>
                INGRES
            </strong>

            <p>
                Processing your query...
            </p>

        </div>

    `;


    messages.appendChild(
        message
    );


    scrollChatToBottom();

}


// ==================================================
// REMOVE LOADING MESSAGE
// ==================================================

function removeLoadingMessage() {

    const loading =
        document.getElementById(
            "loading-message"
        );


    if (loading) {

        loading.remove();

    }

}


// ==================================================
// SEND CHAT QUERY
// ==================================================

async function sendQuery() {

    const input =
        document.getElementById(
            "query-input"
        );


    const sendButton =
        document.getElementById(
            "send-button"
        );


    const query =
        input.value.trim();


    if (!query) {

        return;

    }


    addUserMessage(
        query
    );


    input.value =
        "";


    sendButton.disabled =
        true;


    sendButton.textContent =
        "Sending";


    addLoadingMessage();


    try {

        const response =
            await fetch(

                `${API_URL}/api/chat`,

                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            query:
                                query

                        })

                }

            );


        if (!response.ok) {

            throw new Error(
                `API request failed: ${response.status}`
            );

        }


        const data =
            await response.json();


        removeLoadingMessage();


        if (!data.success) {

            addAssistantMessage(
                "Sorry, I could not process your query."
            );

            updateQueryDetails(
                null
            );

            return;

        }


        addAssistantMessage(
            data.response
        );


        updateQueryDetails(
            data
        );


        updateMapFromResponse(
            data
        );

    }

    catch (error) {

        console.error(
            "INGRES API Error:",
            error
        );


        removeLoadingMessage();


        addAssistantMessage(

            "I could not connect to the INGRES server. " +
            "Please make sure the FastAPI backend is running."

        );


        updateQueryDetails(
            null
        );

    }

    finally {

        sendButton.disabled =
            false;


        sendButton.textContent =
            "Send";


        input.focus();

    }

}


// ==================================================
// UPDATE QUERY DETAILS
// ==================================================

function updateQueryDetails(
    data
) {

    const state =
        document.getElementById(
            "result-state"
        );


    const district =
        document.getElementById(
            "result-district"
        );


    const intent =
        document.getElementById(
            "result-intent"
        );


    const retrieval =
        document.getElementById(
            "result-retrieval"
        );


    const records =
        document.getElementById(
            "stat-records"
        );


    const average =
        document.getElementById(
            "stat-average"
        );


    const maximum =
        document.getElementById(
            "stat-maximum"
        );


    const minimum =
        document.getElementById(
            "stat-minimum"
        );


    if (!data) {

        state.textContent =
            "—";

        district.textContent =
            "—";

        intent.textContent =
            "—";

        retrieval.textContent =
            "—";

        records.textContent =
            "—";

        average.textContent =
            "—";

        maximum.textContent =
            "—";

        minimum.textContent =
            "—";

        return;

    }


    state.textContent =
        data.state ||
        "—";


    district.textContent =
        data.district ||
        "—";


    intent.textContent =
        formatIntent(
            data.intent
        );


    retrieval.textContent =
        data.retrieval_mode ||
        "—";


    const statistics =
        data.statistics ||
        {};


    const totalRecords =
        statistics.total_records !==
        undefined

            ? statistics.total_records

            : statistics.record_count;


    const averageExtraction =
        statistics.average_extraction !==
        undefined

            ? statistics.average_extraction

            : statistics.average;


    const maximumExtraction =
        statistics.maximum_extraction !==
        undefined

            ? statistics.maximum_extraction

            : statistics.maximum;


    const minimumExtraction =
        statistics.minimum_extraction !==
        undefined

            ? statistics.minimum_extraction

            : statistics.minimum;


    records.textContent =
        totalRecords !== undefined
            ? totalRecords
            : "—";


    average.textContent =
        formatPercentage(
            averageExtraction
        );


    maximum.textContent =
        formatPercentage(
            maximumExtraction
        );


    minimum.textContent =
        formatPercentage(
            minimumExtraction
        );

}


// ==================================================
// FORMAT INTENT
// ==================================================

function formatIntent(
    intent
) {

    if (!intent) {

        return "—";

    }


    return intent
        .replaceAll(
            "_",
            " "
        )
        .toLowerCase()
        .replace(
            /\b\w/g,
            function(letter) {

                return letter.toUpperCase();

            }
        );

}


// ==================================================
// FORMAT PERCENTAGE
// ==================================================

function formatPercentage(
    value
) {

    if (
        value === null
        ||
        value === undefined
        ||
        Number.isNaN(
            Number(value)
        )
    ) {

        return "—";

    }


    return (
        `${Number(value).toFixed(2)}%`
    );

}


// ==================================================
// HTML ESCAPE
// ==================================================

function escapeHtml(
    text
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text;


    return div.innerHTML;

}


// ==================================================
// SCROLL CHAT
// ==================================================

function scrollChatToBottom() {

    const messages =
        document.getElementById(
            "chat-messages"
        );


    if (messages) {

        messages.scrollTop =
            messages.scrollHeight;

    }

}


// ==================================================
// DATASET - LOAD
// ==================================================

async function loadDataset() {

    const container =
        document.getElementById(
            "dataset-container"
        );


    if (!container) {

        console.error(
            "Dataset container not found."
        );

        return;

    }


    container.innerHTML = `

        <div style="
            padding:40px;
            text-align:center;
            color:#64748b;
        ">

            Loading groundwater dataset...

        </div>

    `;


    try {

        console.log(
            "Loading dataset..."
        );


        const response =
            await fetch(
                `${API_URL}/api/dataset`
            );


        if (!response.ok) {

            throw new Error(
                `Dataset API failed: ${response.status}`
            );

        }


        const result =
            await response.json();


        console.log(
            "Dataset API response:",
            result
        );


        if (!result.success) {

            throw new Error(
                result.error ||
                "Dataset API returned an error."
            );

        }


        datasetRecords =
            result.data || [];


        datasetColumns =
            result.columns || [];


        datasetCurrentPage =
            1;


        console.log(
            "Dataset records:",
            datasetRecords.length
        );


        console.log(
            "Dataset columns:",
            datasetColumns
        );


        renderDataset();

    }

    catch (error) {

        console.error(
            "Dataset loading error:",
            error
        );


        container.innerHTML = `

            <div style="
                padding:30px;
                background:#fef2f2;
                border:1px solid #fecaca;
                border-radius:8px;
                color:#991b1b;
            ">

                <h3 style="
                    margin-top:0;
                ">

                    Dataset could not be loaded

                </h3>


                <p>

                    ${escapeHtml(
                        error.message
                    )}

                </p>


                <p style="
                    margin-bottom:0;
                ">

                    Make sure FastAPI is running and
                    <strong>
                        /api/dataset
                    </strong>
                    is available.

                </p>

            </div>

        `;

    }

}


// ==================================================
// DATASET - RENDER
// ==================================================

function renderDataset() {

    const container =
        document.getElementById(
            "dataset-container"
        );


    if (!container) {

        return;

    }


    const searchInput =
        document.getElementById(
            "dataset-search"
        );


    const searchTerm =
        searchInput
            ? searchInput.value
                .trim()
                .toLowerCase()
            : "";


    // ----------------------------------------------
    // FILTER
    // ----------------------------------------------

    let filteredRecords =
        datasetRecords;


    if (searchTerm) {

        filteredRecords =
            datasetRecords.filter(
                function(record) {

                    return datasetColumns.some(
                        function(column) {

                            const value =
                                record[column];


                            if (
                                value === null
                                ||
                                value === undefined
                            ) {

                                return false;

                            }


                            return String(value)
                                .toLowerCase()
                                .includes(
                                    searchTerm
                                );

                        }
                    );

                }
            );

    }


    // ----------------------------------------------
    // PAGINATION
    // ----------------------------------------------

    const totalRecords =
        filteredRecords.length;


    const totalPages =
        Math.max(

            1,

            Math.ceil(
                totalRecords /
                DATASET_PAGE_SIZE
            )

        );


    if (
        datasetCurrentPage >
        totalPages
    ) {

        datasetCurrentPage =
            totalPages;

    }


    const startIndex =
        (
            datasetCurrentPage - 1
        ) *
        DATASET_PAGE_SIZE;


    const endIndex =
        Math.min(

            startIndex +
            DATASET_PAGE_SIZE,

            totalRecords

        );


    const pageRecords =
        filteredRecords.slice(
            startIndex,
            endIndex
        );


    // ----------------------------------------------
    // BUILD HTML
    // ----------------------------------------------

    let html = `

        <div style="
            margin-bottom:20px;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:15px;
                flex-wrap:wrap;
            ">

                <div>

                    <h2 style="
                        margin:0 0 5px 0;
                    ">

                        Groundwater Dataset

                    </h2>

                    <div style="
                        color:#64748b;
                    ">

                        ${totalRecords}
                        records found

                    </div>

                </div>


                <input
                    id="dataset-search"
                    type="text"
                    placeholder="Search dataset..."
                    value="${escapeHtml(
                        searchTerm
                    )}"
                    style="
                        width:280px;
                        max-width:100%;
                        padding:11px 14px;
                        border:1px solid #cbd5e1;
                        border-radius:8px;
                        font-size:14px;
                        outline:none;
                    "
                >

            </div>

        </div>

    `;


    // ----------------------------------------------
    // NO RESULTS
    // ----------------------------------------------

    if (
        pageRecords.length === 0
    ) {

        html += `

            <div style="
                padding:30px;
                text-align:center;
                color:#64748b;
                background:#f8fafc;
                border-radius:8px;
            ">

                No matching records found.

            </div>

        `;


        container.innerHTML =
            html;


        attachDatasetSearch();


        return;

    }


    // ----------------------------------------------
    // TABLE
    // ----------------------------------------------

    html += `

        <div style="
            overflow:auto;
            max-height:600px;
            border:1px solid #e2e8f0;
            border-radius:8px;
            background:white;
        ">

            <table style="
                width:100%;
                border-collapse:collapse;
                font-size:13px;
                min-width:1400px;
            ">

                <thead>

                    <tr style="
                        background:#f1f5f9;
                    ">

    `;


    datasetColumns.forEach(
        function(column) {

            html += `

                <th style="
                    position:sticky;
                    top:0;
                    z-index:2;
                    padding:12px 10px;
                    text-align:left;
                    border-bottom:1px solid #cbd5e1;
                    white-space:nowrap;
                    font-weight:600;
                    background:#f1f5f9;
                ">

                    ${escapeHtml(
                        column
                    )}

                </th>

            `;

        }
    );


    html += `

                    </tr>

                </thead>

                <tbody>

    `;


    pageRecords.forEach(
        function(record) {

            html += `

                <tr style="
                    border-bottom:1px solid #e2e8f0;
                ">

            `;


            datasetColumns.forEach(
                function(column) {

                    let value =
                        record[column];


                    if (
                        value === null
                        ||
                        value === undefined
                        ||
                        value === ""
                    ) {

                        value =
                            "—";

                    }


                    // Category column

                    if (
                        column ===
                        "Extraction_Category"
                    ) {

                        const category =
                            normalizeCategory(
                                value
                            );


                        const categoryColor =
                            getCategoryColor(
                                category
                            );


                        html += `

                            <td style="
                                padding:10px;
                                white-space:nowrap;
                            ">

                                <span style="
                                    display:inline-block;
                                    padding:4px 8px;
                                    border-radius:5px;
                                    background:${categoryColor};
                                    color:white;
                                    font-weight:600;
                                    font-size:12px;
                                ">

                                    ${escapeHtml(
                                        category
                                    )}

                                </span>

                            </td>

                        `;

                    }

                    else {

                        html += `

                            <td style="
                                padding:10px;
                                white-space:nowrap;
                                color:#334155;
                            ">

                                ${escapeHtml(
                                    String(value)
                                )}

                            </td>

                        `;

                    }

                }
            );


            html += `

                </tr>

            `;

        }
    );


    html += `

                </tbody>

            </table>

        </div>

    `;


    // ----------------------------------------------
    // PAGINATION
    // ----------------------------------------------

    html += `

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-top:15px;
            gap:10px;
            flex-wrap:wrap;
        ">

            <div style="
                color:#64748b;
                font-size:13px;
            ">

                Showing
                ${startIndex + 1}
                -
                ${endIndex}
                of
                ${totalRecords}

            </div>


            <div style="
                display:flex;
                align-items:center;
                gap:8px;
            ">

                <button
                    id="dataset-prev"
                    ${datasetCurrentPage <= 1
                        ? "disabled"
                        : ""}
                    style="
                        padding:8px 13px;
                        border:1px solid #cbd5e1;
                        border-radius:6px;
                        background:white;
                        cursor:pointer;
                    "
                >

                    Previous

                </button>


                <span style="
                    font-size:13px;
                    color:#475569;
                ">

                    Page
                    ${datasetCurrentPage}
                    of
                    ${totalPages}

                </span>


                <button
                    id="dataset-next"
                    ${datasetCurrentPage >= totalPages
                        ? "disabled"
                        : ""}
                    style="
                        padding:8px 13px;
                        border:1px solid #cbd5e1;
                        border-radius:6px;
                        background:white;
                        cursor:pointer;
                    "
                >

                    Next

                </button>

            </div>

        </div>

    `;


    container.innerHTML =
        html;


    attachDatasetSearch();


    // ----------------------------------------------
    // PREVIOUS
    // ----------------------------------------------

    const previousButton =
        document.getElementById(
            "dataset-prev"
        );


    if (previousButton) {

        previousButton.addEventListener(
            "click",
            function() {

                if (
                    datasetCurrentPage > 1
                ) {

                    datasetCurrentPage--;

                    renderDataset();

                }

            }
        );

    }


    // ----------------------------------------------
    // NEXT
    // ----------------------------------------------

    const nextButton =
        document.getElementById(
            "dataset-next"
        );


    if (nextButton) {

        nextButton.addEventListener(
            "click",
            function() {

                if (
                    datasetCurrentPage <
                    totalPages
                ) {

                    datasetCurrentPage++;

                    renderDataset();

                }

            }
        );

    }

}


// ==================================================
// DATASET SEARCH
// ==================================================

function attachDatasetSearch() {

    const searchInput =
        document.getElementById(
            "dataset-search"
        );


    if (!searchInput) {

        return;

    }


    searchInput.addEventListener(
        "input",
        function() {

            datasetCurrentPage =
                1;


            renderDataset();


            const newInput =
                document.getElementById(
                    "dataset-search"
                );


            if (newInput) {

                newInput.focus();


                newInput.setSelectionRange(

                    newInput.value.length,

                    newInput.value.length

                );

            }

        }
    );

}


// ==================================================
// DATASET TAB INITIALIZATION
// ==================================================

function initializeDatasetTab() {

    const container =
        document.getElementById(
            "dataset-container"
        );


    if (!container) {

        console.error(
            "dataset-container does not exist in index.html"
        );

        return;

    }


    if (datasetLoaded) {

        return;

    }


    datasetLoaded =
        true;


    loadDataset();

}


// ==================================================
// INITIALIZATION
// ==================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const input =
            document.getElementById(
                "query-input"
            );


        if (input) {

            input.focus();

        }


        // Initialize map

        initializeIndiaMap();

    }
);