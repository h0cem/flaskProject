// dynamically set height and width to that of parent element
parentElement = document.getElementById("d3-graph").parentElement
var w = 900//parentElement.offsetWidth;
var h = 700//parentElement.offsetHeight;

var svg;

// D3 variables
var svgSelection;
var gSelection;
var nodeSelection;
var linkSelection;
var circleSelection;
var textSelection;
var simulation;

var focusNode = null,
    highlightNode = null;

var textCenter = false;
var outline = false;

var textColor = 'rgb(255,255,255)';

var linkHighlightColor = "rgb(24,39,81)";
var highlightTrans = 0.1;

var size = d3.scalePow().exponent(1)
    .domain([1, 100])
    .range([8, 24]);

// Nodes Colors
const InfectedPersonColor = "#730f0f";
const SusceptiblePersonColor = "#175f18";
const CompanyColor = "#a98803";

// Edges Colors
const Person_Person = "#154d98";
const Person_Facility = "#545437";

// const inactiveLinkColor = "rgb(255,211,0)";


const onHoverNonConnectedFontWeight = "normal";
const onHoverConnectedFontWeight = "bold";
const onHoverConnectedFontStyle = "italic";
const onHoverNonConnectedFontStyle = "normal";


var nominalBaseNodeSize = 10;
var nominalTextSize = 10;
var maxTextSize = 24;
var nominalStroke = 2;
var maxStroke = 4.5;
var maxBaseNodeSize = 36;
var minZoom = 0.1;
var maxZoom = 7;
var zoom = d3.zoom().scaleExtent([minZoom, maxZoom]);

var distance = 50

svgSelection = d3.select("#d3-graph")
    .append("svg")
    .attr("class", "graph-svg")
    .attr("width", w)
    .attr("height", h)

gSelection = svgSelection.append("g");

function createSimulation() {
    simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id((d) => {
                return d.id
            })
                .distance((d) => {
                    if (d.hasOwnProperty('distance'))
                        return distance * d.distance
                    else
                        return distance
                })
        )
        .force("charge", d3.forceManyBody().strength(-500))
        .force("center", d3.forceCenter(w / 2, h / 2));
}

createSimulation()

function createJSON() {
    d3.json("/data", function (error, graph) {
        if (error) throw error;
        graph = graph.data
        update(graph.links, graph.nodes)
    });
}

createJSON()

function update(dataLinks, dataNodes) {

    var linkedByIndex = {};

    var tocolor = "fill";
    var towhite = "stroke";
    if (outline) {
        tocolor = "stroke";
        towhite = "fill";
    }

    dataLinks.forEach(populateLinkedByIndex);

    function updateForceData() {
        simulation
            .nodes(dataNodes)
            .on("tick", tick);

        simulation.force("link")
            .links(dataLinks);
    }

    function tick() {
        linkSelection
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        nodeSelection
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
    }

    function createLinkSelection() {
        linkSelection = gSelection.append("g")
            .attr("class", "links")
            .selectAll(".link")
            .data(dataLinks)
            .enter().append("line")
            .style("stroke-dasharray", (d) => {
                if (d.hasOwnProperty('distance')) {
                    return "6, 1"
                }
            })
            .style("stroke-width", nominalStroke)
            .style("stroke", (d) => {
                if (d.hasOwnProperty('distance')) {
                    return Person_Person
                } else
                    return Person_Facility
            })
    }

    function createNodeSelection() {
        nodeSelection = gSelection.append("g")
            .attr("class", "nodes")
            .selectAll(".node")
            .data(dataNodes)
            .enter().append("g")
            .attr("class", "node")
    }

    function createNode() {
        circleSelection = nodeSelection.append("path")
            .attr('title', function (d) {
                return JSON.stringify(d, null, 4)
                /*                if (d.type === "person")
                                    return JSON.stringify((({id, type, status, risk, weight}) => ({
                                        id,
                                        type,
                                        status,
                                        risk,
                                        weight
                                    }))(d), null, 4)
                                else
                                    return JSON.stringify((({id, type, min_person, PNB, weight}) => ({
                                        id,
                                        type,
                                        min_person,
                                        PNB,
                                        weight
                                    }))(d), null, 4)*/
            })
            .attr("d", d3.symbol()
                .size((d) => {
                    if (d.type === "person") {
                        return d.risk * 40
                    } else {
                        return 250
                    }
                })
                .type((d) => {
                    if (d.type === "person") {
                        console.log(d)
                        return d3.symbolCircle;
                    } else {
                        return d3.symbolSquare;
                    }
                }))
            .style("fill", (d) => {
                if (d.type === "person")
                    if (d.status === "I")
                        return InfectedPersonColor
                    else
                        return SusceptiblePersonColor
                else
                    return CompanyColor
            })
            .style("stroke-width", 0)
    }

    function createText() {
        textSelection = nodeSelection.append("text")
            .text(function (d) {
                return d.id;
            })
            .attr('x', 9)
            .attr('y', 5)
            .append("title")
            .text(function (d) {
                return d.id;
            })
    }

    function styleText() {
        textSelection
            .style("font-size", nominalTextSize + "px")
            .style("font-color", textColor)
        if (textCenter)
            textSelection.text(function (d) {
                return d.id;
            })
                .style("text-anchor", "middle");
        else
            textSelection.attr("dx", function (d) {
                return (size(d.size) || nominalBaseNodeSize);
            })
                .text(function (d) {
                    return '\u2002' + d.id;
                });
    }

    function setNodeEvents() {
        nodeSelection
            .on("dblclick", onNodeDoubleClick)
            .on("mouseover", onNodeMouseOver)
            .on("mouseout", onNodeMouseOut)
        nodeSelection.call(d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded)
        )
    }

    function dragStarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
        focusNode = d;
        console.log(focusNode)
        setFocus(d);
        if (highlightNode === null) {
            setHighlight(d);
        }
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragEnded(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
        if (focusNode !== null) {
            focusNode = null;
            if (highlightTrans < 1) {
                circleSelection.style("opacity", 1);
                textSelection.style("opacity", 1);
                linkSelection.style("opacity", 1);
            }
        }
        if (highlightNode === null) {
            exitHighlight();
        }
    }

    function onNodeDoubleClick(node) {
        gSelection.call(d3.zoom().on("zoom", () => {
            let k = 2
            var dcx = (w / 2 - node.x * k);
            var dcy = (h / 2 - node.y * k);
            zoom.translateExtent([[0, 0], [w, h]])
            gSelection.attr("transform", "translate(" + dcx + "," + dcy + ")scale(" + k + ")");
        }))
    }

    function onNodeMouseOver(node) {
        setHighlight(node);
        tippy('svg g g path', {
            allowHTML: false,
            animation: 'scale',
            arrow: true,
            arrowType: 'round',
            delay: 100,
            duration: 500,
            size: 'small',
            sticky: true
        })
    }

    function onNodeMouseOut() {
        exitHighlight();
    }

    function zoomed() {
        svgSelection.call(d3.zoom().on("zoom", () => {
            let k = d3.event.transform.k
            var stroke = nominalStroke;
            if (nominalStroke * k > maxStroke) stroke = maxStroke / k;
            linkSelection.style("stroke-width", stroke);

            var baseRadius = nominalBaseNodeSize;
            if (nominalBaseNodeSize * k > maxBaseNodeSize) baseRadius = maxBaseNodeSize / k;
            circleSelection.attr("d", d3.symbol()
                .size((d) => {
                    if (d.type === "person") {
                        return d.risk * 40
                    } else {
                        return 250
                    }
                })
                .type((d) => {
                    if (d.type === "person") {
                        return d3.symbolCircle;
                    } else {
                        return d3.symbolSquare;
                    }
                }))

            if (!textCenter) textSelection.attr("dx", function (d) {
                return (size(d.size) * baseRadius / nominalBaseNodeSize || baseRadius);
            });

            var textSize = nominalTextSize;
            if (nominalTextSize * k > maxTextSize) textSize = maxTextSize / k;
            textSelection.style("font-size", textSize + "px");

            gSelection.attr("transform", d3.event.transform)
        }))
    }

    function setHighlight(node) {
        svgSelection.style("cursor", "pointer");
        if (focusNode !== null) node = focusNode;
        console.log(focusNode)
        highlightNode = node;

        if (linkHighlightColor !== "white") {
            circleSelection.style(towhite, (o) => {
                return isConnected(node, o) ? linkHighlightColor : "white";
            });
            textSelection.style("font-style", function (o) {
                if (isConnected(node, o)) {
                    return onHoverConnectedFontStyle;
                } else {
                    return onHoverNonConnectedFontStyle;
                }
            });
            textSelection.style("font-weight", function (o) {
                if (isConnected(node, o)) {
                    return onHoverConnectedFontWeight;
                } else {
                    return onHoverNonConnectedFontWeight;
                }
            });
            linkSelection.style("stroke", function (o) {
                return o.source.index === node.index || o.target.index === node.index
                    ? linkHighlightColor : o.hasOwnProperty('distance')
                        ? Person_Person : Person_Facility
            });
        }
    }

    function setFocus(d) {
        if (highlightTrans < 1) {
            circleSelection.style("opacity", (o) => {
                return isConnected(d, o) ? 1 : highlightTrans;
            });

            textSelection.style("opacity", (o) => {
                return isConnected(d, o) ? 1 : highlightTrans;
            })
                .style("color", "rgb(190,0,0)");

            linkSelection.style("opacity", (o) => {
                return o.source.index === d.index || o.target.index === d.index
                    ? 1 : highlightTrans;
            });
        }
    }

    function isConnected(node1, node2) {
        return linkedByIndex[node1.index + "," + node2.index]
            || linkedByIndex[node2.index + "," + node1.index]
            || node1.index === node2.index;
    }

    /*
        function hasConnections(node) {
            for (var property in linkedByIndex) {
                s = property.split(",");
                if ((s[0] == node.index || s[1] == node.index) && linkedByIndex[property])
                    return true;
            }
            return false;
        }
    */

    function populateLinkedByIndex(link) {
        linkedByIndex[link.source + "," + link.target] = true;
    }

    function exitHighlight() {
        highlightNode = null;
        if (focusNode === null) {
            svgSelection.style("cursor", "default");
            if (linkHighlightColor !== "white") {
                circleSelection.style(towhite, "white");
                textSelection.style("font-style", "normal");
                textSelection.style("font-weight", "normal");
                linkSelection.style("stroke", function (o) {
                    return o.hasOwnProperty('distance') ? Person_Person : Person_Facility
                });
            }
        }
    }

    createLinkSelection()
    createNodeSelection()
    createNode()
    updateForceData()
    setNodeEvents()
    createText()
    styleText()
    zoomed()
    /*
    * TODO:
    *  1.visualise by type
    * */
}






