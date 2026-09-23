import 'dart:async';

import 'package:flutter/material.dart';

import '../services/app_theme_controller.dart';
import '../services/dashboard_firebase_service.dart';
import '../services/traffic_api.dart';


// ============================================================
// SMART TRAFFIC AI - COLORS
// ============================================================

const Color roadDark = Color(0xFF101418);
const Color roadSurface = Color(0xFF171C21);
const Color trafficPanel = Color(0xFF1B2229);
const Color laneWhite = Color(0xFFE5E7EB);

const Color signalRed = Color(0xFFFF3B30);
const Color signalYellow = Color(0xFFFFC107);
const Color signalGreen = Color(0xFF00E676);

const Color aiCyan = Color(0xFF00D9FF);
const Color trafficBlue = Color(0xFF2196F3);

const Color pedestrianPurple = Color(0xFFB56CFF);
const Color warningOrange = Color(0xFFFF8A00);


// ============================================================
// DASHBOARD SCREEN
// ============================================================

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}


// ============================================================
// DASHBOARD STATE
// ============================================================

class _DashboardScreenState extends State<DashboardScreen> {

  // ----------------------------------------------------------
  // NAVIGATION
  // ----------------------------------------------------------

  int selectedIndex = 0;


  // ----------------------------------------------------------
  // API DATA
  // ----------------------------------------------------------

  Map<String, dynamic> trafficData = {};

  Map<String, dynamic> systemData = {};
  Map<String, dynamic> cameraData = {};

  bool apiOnline = false;

  String apiError = "";

  Timer? refreshTimer;


  // ----------------------------------------------------------
  // LIFECYCLE
  // ----------------------------------------------------------

  @override
  void initState() {
    super.initState();

    _loadTrafficData();

    refreshTimer = Timer.periodic(
      const Duration(seconds: 2),
      (_) {
        _loadTrafficData();
      },
    );
  }


  @override
  void dispose() {
    refreshTimer?.cancel();
    super.dispose();
  }


  // ==========================================================
  // LOAD TRAFFIC DATA
  // ==========================================================

  Future<void> _loadTrafficData() async {

    try {

      final traffic =
          await TrafficApi.getTrafficStatus();

      Map<String, dynamic> system = {};

      try {
        system =
            await TrafficApi.getSystemStatus();
      } catch (_) {
        system = {};
      }

      if (!mounted) return;

      setState(() {

        trafficData =
            Map<String, dynamic>.from(traffic);

        systemData =
            Map<String, dynamic>.from(system);

        apiOnline = true;

        apiError = "";

      });

      await DashboardFirebaseService.saveLatestDashboardSnapshot(
        trafficData: trafficData,
        systemData: systemData,
        apiOnline: true,
        apiError: "",
      );

    } catch (e) {

      if (!mounted) return;

      setState(() {

        apiOnline = false;

        apiError = e.toString();

      });

      await DashboardFirebaseService.saveLatestDashboardSnapshot(
        trafficData: trafficData,
        systemData: systemData,
        apiOnline: false,
        apiError: e.toString(),
      );
    }
  }


  // ==========================================================
  // PAGE SELECTOR
  // ==========================================================

  Widget _buildCurrentPage() {

    switch (selectedIndex) {

      case 0:
        return _buildOverviewPage();

      case 1:
        return _buildCamerasPage();

      case 2:
        return _buildAnalyticsPage();

      case 3:
        return _buildSettingsPage();

      default:
        return _buildOverviewPage();
    }
  }


  // ==========================================================
  // MAIN BUILD
  // ==========================================================

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      backgroundColor: roadDark,

      appBar: _buildAppBar(),

      body: _buildCurrentPage(),

      bottomNavigationBar:
          _buildBottomNavigation(),

    );
  }


  // ==========================================================
  // APP BAR
  // ==========================================================

  PreferredSizeWidget _buildAppBar() {

    return AppBar(

      backgroundColor: roadSurface,

      elevation: 0,

      titleSpacing: 16,

      title: Row(
        children: [

          Container(
            padding: const EdgeInsets.all(8),

            decoration: BoxDecoration(
              color: aiCyan.withOpacity(0.12),
              borderRadius:
                  BorderRadius.circular(10),
            ),

            child: const Icon(
              Icons.traffic,
              color: aiCyan,
              size: 24,
            ),
          ),

          const SizedBox(width: 12),

          const Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,

            children: [

              Text(
                "Smart Traffic AI",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),

              Text(
                "AI Adaptive Traffic Control",
                style: TextStyle(
                  color: Colors.white54,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ],
      ),

      actions: [

        Container(
          margin: const EdgeInsets.only(
            right: 14,
          ),

          child: Center(
            child: Container(
              padding:
                  const EdgeInsets.symmetric(
                horizontal: 10,
                vertical: 6,
              ),

              decoration: BoxDecoration(
                color: apiOnline
                    ? signalGreen.withOpacity(0.12)
                    : signalRed.withOpacity(0.12),

                borderRadius:
                    BorderRadius.circular(20),

                border: Border.all(
                  color: apiOnline
                      ? signalGreen.withOpacity(0.4)
                      : signalRed.withOpacity(0.4),
                ),
              ),

              child: Row(
                children: [

                  Icon(
                    Icons.circle,
                    size: 8,
                    color: apiOnline
                        ? signalGreen
                        : signalRed,
                  ),

                  const SizedBox(width: 6),

                  Text(
                    apiOnline
                        ? "API ONLINE"
                        : "OFFLINE",

                    style: TextStyle(
                      color: apiOnline
                          ? signalGreen
                          : signalRed,

                      fontSize: 10,

                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }


  // ==========================================================
  // BOTTOM NAVIGATION
  // ==========================================================

  Widget _buildBottomNavigation() {

    return BottomNavigationBar(

      currentIndex: selectedIndex,

      onTap: (index) {

        setState(() {
          selectedIndex = index;
        });

      },

      type: BottomNavigationBarType.fixed,

      backgroundColor: trafficPanel,

      selectedItemColor: aiCyan,

      unselectedItemColor:
          Colors.white54,

      selectedFontSize: 12,

      unselectedFontSize: 11,

      items: const [

        BottomNavigationBarItem(
          icon: Icon(Icons.dashboard),
          label: "Overview",
        ),

        BottomNavigationBarItem(
          icon: Icon(Icons.videocam),
          label: "Cameras",
        ),

        BottomNavigationBarItem(
          icon: Icon(Icons.analytics),
          label: "Analytics",
        ),

        BottomNavigationBarItem(
          icon: Icon(Icons.settings),
          label: "Settings",
        ),
      ],
    );
  }


  // ==========================================================
  // OVERVIEW PAGE
  // ==========================================================

  Widget _buildOverviewPage() {

    final int vehicles =
        trafficData["vehicles_detected"] ?? 0;

    final int pedestrians =
        trafficData["pedestrians_detected"] ?? 0;

    final int pedestriansWaiting =
        trafficData["pedestrians_waiting"] ?? 0;

    final int pedestriansCrossing =
        trafficData["pedestrians_crossing"] ?? 0;

    final String activeSignal =
        trafficData["active_signal"] ??
            "UNKNOWN";

    final String priority =
        trafficData["priority_direction"] ??
            "UNKNOWN";

    final String trafficStatus =
        trafficData["traffic_status"] ??
            "UNKNOWN";

    final int greenTime =
        trafficData["green_time"] ?? 0;

    final String controlMode =
        trafficData["control_mode"] ??
            "ADAPTIVE AI";

    final bool signalSwitched =
        trafficData["signal_switched"] ??
            false;

    final double simulationTime =
        (trafficData["simulation_time"] ?? 0)
            .toDouble();


    return RefreshIndicator(

      onRefresh: _loadTrafficData,

      color: aiCyan,

      backgroundColor: trafficPanel,

      child: SingleChildScrollView(

        physics:
            const AlwaysScrollableScrollPhysics(),

        padding:
            const EdgeInsets.all(16),

        child: Column(

          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [

            // ------------------------------------------------
            // HEADER
            // ------------------------------------------------

            _sectionHeader(
              "Traffic Control Center",
              "Real-time AI intersection monitoring",
              Icons.dashboard,
            ),

            const SizedBox(height: 18),


            // ------------------------------------------------
            // SUMMARY CARDS
            // ------------------------------------------------

            LayoutBuilder(
              builder:
                  (context, constraints) {

                final bool wide =
                    constraints.maxWidth > 700;

                if (wide) {

                  return Row(
                    children: [

                      Expanded(
                        child:
                            _summaryCard(
                          "Vehicles",
                          "$vehicles",
                          Icons.directions_car,
                          trafficBlue,
                        ),
                      ),

                      const SizedBox(width: 12),

                      Expanded(
                        child:
                            _summaryCard(
                          "Pedestrians",
                          "$pedestrians",
                          Icons.directions_walk,
                          pedestrianPurple,
                        ),
                      ),

                      const SizedBox(width: 12),

                      Expanded(
                        child:
                            _summaryCard(
                          "Priority",
                          priority,
                          Icons.priority_high,
                          signalGreen,
                        ),
                      ),

                      const SizedBox(width: 12),

                      Expanded(
                        child:
                            _summaryCard(
                          "Traffic",
                          trafficStatus,
                          Icons.traffic,
                          _trafficStatusColor(
                            trafficStatus,
                          ),
                        ),
                      ),
                    ],
                  );
                }

                return Column(
                  children: [

                    Row(
                      children: [

                        Expanded(
                          child:
                              _summaryCard(
                            "Vehicles",
                            "$vehicles",
                            Icons.directions_car,
                            trafficBlue,
                          ),
                        ),

                        const SizedBox(width: 10),

                        Expanded(
                          child:
                              _summaryCard(
                            "Pedestrians",
                            "$pedestrians",
                            Icons.directions_walk,
                            pedestrianPurple,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 10),

                    Row(
                      children: [

                        Expanded(
                          child:
                              _summaryCard(
                            "Priority",
                            priority,
                            Icons.priority_high,
                            signalGreen,
                          ),
                        ),

                        const SizedBox(width: 10),

                        Expanded(
                          child:
                              _summaryCard(
                            "Traffic",
                            trafficStatus,
                            Icons.traffic,
                            _trafficStatusColor(
                              trafficStatus,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              },
            ),


            const SizedBox(height: 20),


            // ------------------------------------------------
            // SUMO SIMULATION DEMO
            // ------------------------------------------------

            _sectionHeader(
              "SUMO Simulation Demo",
              "Live intersection behavior powered by SUMO TraCI",
              Icons.play_circle_fill,
            ),

            const SizedBox(height: 12),

            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 10,
              ),
              decoration: BoxDecoration(
                color: aiCyan.withOpacity(0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: aiCyan.withOpacity(0.22),
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.sensors,
                    color: aiCyan,
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      "Demo status: SUMO is running and updating signal priority in real time.",
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.85),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: signalGreen.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      "LIVE",
                      style: TextStyle(
                        color: signalGreen,
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 18),

            _buildJudgeDemoCard(),

            const SizedBox(height: 18),

            // ------------------------------------------------
            // TRAFFIC OVERVIEW
            // ------------------------------------------------

            _sectionHeader(
              "Traffic Overview",
              "Vehicle demand by direction",
              Icons.alt_route,
            ),

            const SizedBox(height: 12),

            _buildDirectionGrid(),


            const SizedBox(height: 20),


            // ------------------------------------------------
            // SIGNAL + AI DECISION
            // ------------------------------------------------

            LayoutBuilder(
              builder:
                  (context, constraints) {

                if (constraints.maxWidth > 750) {

                  return Row(
                    crossAxisAlignment:
                        CrossAxisAlignment.start,

                    children: [

                      Expanded(
                        child:
                            _buildIntersectionCard(
                          activeSignal,
                          priority,
                        ),
                      ),

                      const SizedBox(width: 14),

                      Expanded(
                        child:
                            _buildAIDecisionCard(
                          priority,
                          controlMode,
                          greenTime,
                          signalSwitched,
                        ),
                      ),
                    ],
                  );
                }

                return Column(
                  children: [

                    _buildIntersectionCard(
                      activeSignal,
                      priority,
                    ),

                    const SizedBox(height: 14),

                    _buildAIDecisionCard(
                      priority,
                      controlMode,
                      greenTime,
                      signalSwitched,
                    ),
                  ],
                );
              },
            ),


            const SizedBox(height: 20),


            // ------------------------------------------------
            // PEDESTRIAN MONITOR
            // ------------------------------------------------

            _buildPedestrianCard(
              pedestrians,
              pedestriansWaiting,
              pedestriansCrossing,
            ),


            const SizedBox(height: 20),


            // ------------------------------------------------
            // SYSTEM STATUS
            // ------------------------------------------------

            _buildSystemStatusCard(),


            const SizedBox(height: 20),


            // ------------------------------------------------
            // SIMULATION STATUS
            // ------------------------------------------------

            _buildSimulationCard(
              simulationTime,
              activeSignal,
              priority,
            ),


            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }


  // ==========================================================
  // JUDGE DEMO CARD
  // ==========================================================

  Widget _buildJudgeDemoCard() {
    final String activeSignal =
        trafficData["active_signal"] ?? "UNKNOWN";

    final String priority =
        trafficData["priority_direction"] ?? "UNKNOWN";

    final String trafficStatus =
        trafficData["traffic_status"] ?? "UNKNOWN";

    final int greenTime =
        trafficData["green_time"] ?? 0;

    final double simulationTime =
        (trafficData["simulation_time"] ?? 0).toDouble();

    final bool isGreen = activeSignal.toUpperCase().contains("NORTH") ||
        activeSignal.toUpperCase().contains("EAST") ||
        activeSignal.toUpperCase().contains("SOUTH") ||
        activeSignal.toUpperCase().contains("WEST");

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: trafficPanel,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: signalGreen.withOpacity(0.22),
        ),
        boxShadow: [
          BoxShadow(
            color: signalGreen.withOpacity(0.10),
            blurRadius: 18,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: (isGreen ? signalGreen : signalRed).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  Icons.play_arrow_rounded,
                  color: isGreen ? signalGreen : signalRed,
                  size: 22,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  "SUMO Demo",
                  style: TextStyle(
                    color: isGreen ? signalGreen : signalRed,
                    fontSize: 19,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: signalGreen.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Text(
                  "LIVE",
                  style: TextStyle(
                    color: signalGreen,
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            "Signal cycle: $activeSignal is active. Priority is $priority and traffic level is $trafficStatus.",
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: _miniDemoStat(
                  "Signal",
                  activeSignal,
                  isGreen ? signalGreen : signalRed,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _miniDemoStat(
                  "Green",
                  "${greenTime}s",
                  aiCyan,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _miniDemoStat(
                  "Time",
                  "${simulationTime.toStringAsFixed(1)}s",
                  pedestrianPurple,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              const Icon(
                Icons.lightbulb_outline,
                color: signalYellow,
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                "Demo script: traffic rises → signal priority switches → adaptive timing updates.",
                style: TextStyle(
                  color: Colors.white.withOpacity(0.7),
                  fontSize: 11,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _miniDemoStat(
    String title,
    String value,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.25),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: Colors.white38,
              fontSize: 9,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 13,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  // ==========================================================
  // SECTION HEADER
  // ==========================================================

  Widget _sectionHeader(
    String title,
    String subtitle,
    IconData icon,
  ) {

    return Row(
      children: [

        Container(
          padding: const EdgeInsets.all(10),

          decoration: BoxDecoration(
            color:
                aiCyan.withOpacity(0.10),

            borderRadius:
                BorderRadius.circular(12),
          ),

          child: Icon(
            icon,
            color: aiCyan,
            size: 22,
          ),
        ),

        const SizedBox(width: 12),

        Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,

            children: [

              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 3),

              Text(
                subtitle,
                style: const TextStyle(
                  color: Colors.white54,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }


  // ==========================================================
  // SUMMARY CARD
  // ==========================================================

  Widget _summaryCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {

    return Container(
      padding:
          const EdgeInsets.all(16),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),

        border: Border.all(
          color: color.withOpacity(0.20),
        ),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Row(
            mainAxisAlignment:
                MainAxisAlignment.spaceBetween,

            children: [

              Icon(
                icon,
                color: color,
                size: 26,
              ),

              Container(
                width: 8,
                height: 8,

                decoration:
                    BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 4),

          Text(
            title,
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // DIRECTION GRID
  // ==========================================================

  Widget _buildDirectionGrid() {

    final directions =
        (trafficData["directions"] ?? {})
            as Map<String, dynamic>;

    final names = [
      "NORTH",
      "SOUTH",
      "EAST",
      "WEST",
    ];

    return GridView.builder(

      shrinkWrap: true,

      physics:
          const NeverScrollableScrollPhysics(),

      itemCount: names.length,

      gridDelegate:
          const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
        childAspectRatio: 1.65,
      ),

      itemBuilder:
          (context, index) {

        final name = names[index];

        final data =
            directions[name] ?? {};

        return _directionCard(
          name,
          data,
        );
      },
    );
  }


  // ==========================================================
  // DIRECTION CARD
  // ==========================================================

  Widget _directionCard(
    String direction,
    dynamic rawData,
  ) {

    final Map<String, dynamic> data =
        rawData is Map
            ? Map<String, dynamic>.from(
                rawData,
              )
            : {};

    final int vehicles =
        data["vehicles"] ?? 0;

    final int queue =
        data["queue"] ?? 0;

    final double waiting =
        (data["waiting_time"] ?? 0)
            .toDouble();

    final String status =
        data["status"] ?? "LOW";

    final Color statusColor =
        _trafficStatusColor(status);

    IconData directionIcon;

    switch (direction) {

      case "NORTH":
        directionIcon =
            Icons.arrow_upward;

        break;

      case "SOUTH":
        directionIcon =
            Icons.arrow_downward;

        break;

      case "EAST":
        directionIcon =
            Icons.arrow_forward;

        break;

      default:
        directionIcon =
            Icons.arrow_back;
    }

    return Container(

      padding:
          const EdgeInsets.all(14),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),

        border: Border.all(
          color:
              statusColor.withOpacity(0.20),
        ),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Row(
            children: [

              Icon(
                directionIcon,
                color: aiCyan,
                size: 20,
              ),

              const SizedBox(width: 8),

              Expanded(
                child: Text(
                  direction,
                  style:
                      const TextStyle(
                    color: Colors.white,
                    fontWeight:
                        FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),

              Container(
                padding:
                    const EdgeInsets.symmetric(
                  horizontal: 7,
                  vertical: 3,
                ),

                decoration:
                    BoxDecoration(
                  color:
                      statusColor.withOpacity(
                    0.12,
                  ),
                  borderRadius:
                      BorderRadius.circular(10),
                ),

                child: Text(
                  status,
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 9,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),

          const Spacer(),

          Row(
            mainAxisAlignment:
                MainAxisAlignment.spaceBetween,

            children: [

              _smallMetric(
                "Cars",
                "$vehicles",
              ),

              _smallMetric(
                "Queue",
                "$queue",
              ),

              _smallMetric(
                "Wait",
                "${waiting.toStringAsFixed(1)}s",
              ),
            ],
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // SMALL METRIC
  // ==========================================================

  Widget _smallMetric(
    String title,
    String value,
  ) {

    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,

      children: [

        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 15,
            fontWeight: FontWeight.bold,
          ),
        ),

        Text(
          title,
          style: const TextStyle(
            color: Colors.white38,
            fontSize: 9,
          ),
        ),
      ],
    );
  }


  // ==========================================================
  // INTERSECTION CARD
  // ==========================================================

  Widget _buildIntersectionCard(
    String activeSignal,
    String priority,
  ) {

    final bool nsActive =
        activeSignal == "NORTH/SOUTH";

    final bool ewActive =
        activeSignal == "EAST/WEST";

    return Container(

      padding:
          const EdgeInsets.all(18),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(18),

        border: Border.all(
          color:
              aiCyan.withOpacity(0.18),
        ),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Row(
            children: [

              const Icon(
                Icons.traffic,
                color: aiCyan,
              ),

              const SizedBox(width: 10),

              const Expanded(
                child: Text(
                  "SUMO Live Demo",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 17,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: aiCyan.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Text(
                  "TraCI",
                  style: TextStyle(
                    color: aiCyan,
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // ------------------------------------------------
          // INTERSECTION VISUAL
          // ------------------------------------------------

          SizedBox(
            height: 230,

            child: Stack(
              alignment: Alignment.center,

              children: [

                // Vertical road

                Positioned(
                  top: 0,
                  bottom: 0,
                  left: 80,
                  right: 80,

                  child: Container(
                    color: roadDark,
                  ),
                ),

                // Horizontal road

                Positioned(
                  left: 0,
                  right: 0,
                  top: 80,
                  bottom: 80,

                  child: Container(
                    color: roadDark,
                  ),
                ),

                // Center

                Container(
                  width: 95,
                  height: 95,

                  decoration: BoxDecoration(
                    color: roadSurface,
                    borderRadius:
                        BorderRadius.circular(8),
                  ),
                ),

                // North signal

                Positioned(
                  top: 18,
                  child: _signalLight(
                    nsActive
                        ? signalGreen
                        : signalRed,
                  ),
                ),

                // South signal

                Positioned(
                  bottom: 18,
                  child: _signalLight(
                    nsActive
                        ? signalGreen
                        : signalRed,
                  ),
                ),

                // East signal

                Positioned(
                  right: 18,
                  child: _signalLight(
                    ewActive
                        ? signalGreen
                        : signalRed,
                  ),
                ),

                // West signal

                Positioned(
                  left: 18,
                  child: _signalLight(
                    ewActive
                        ? signalGreen
                        : signalRed,
                  ),
                ),

                // Center AI

                Container(
                  width: 58,
                  height: 58,

                  decoration:
                      BoxDecoration(
                    color:
                        aiCyan.withOpacity(
                      0.10,
                    ),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color:
                          aiCyan.withOpacity(
                        0.6,
                      ),
                    ),
                  ),

                  child: const Icon(
                    Icons.smart_toy,
                    color: aiCyan,
                    size: 28,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 12),

          Row(
            children: [

              const Icon(
                Icons.priority_high,
                color: signalGreen,
                size: 18,
              ),

              const SizedBox(width: 7),

              Text(
                "AI Priority: $priority",
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // SIGNAL LIGHT
  // ==========================================================

  Widget _signalLight(Color color) {

    return Container(
      width: 22,
      height: 22,

      decoration: BoxDecoration(
        color: color,

        shape: BoxShape.circle,

        boxShadow: [
          BoxShadow(
            color:
                color.withOpacity(0.6),
            blurRadius: 12,
            spreadRadius: 2,
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // AI DECISION CARD
  // ==========================================================

  Widget _buildAIDecisionCard(
    String priority,
    String controlMode,
    int greenTime,
    bool signalSwitched,
  ) {

    return Container(

      padding:
          const EdgeInsets.all(18),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(18),

        border: Border.all(
          color:
              aiCyan.withOpacity(0.22),
        ),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Row(
            children: [

              Container(
                padding:
                    const EdgeInsets.all(9),

                decoration:
                    BoxDecoration(
                  color:
                      aiCyan.withOpacity(0.10),
                  borderRadius:
                      BorderRadius.circular(10),
                ),

                child: const Icon(
                  Icons.psychology,
                  color: aiCyan,
                ),
              ),

              const SizedBox(width: 10),

              const Text(
                "AI Signal Decision",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          const SizedBox(height: 18),

          _decisionItem(
            "Priority Direction",
            priority,
            Icons.priority_high,
            aiCyan,
          ),

          _decisionItem(
            "Control Mode",
            controlMode,
            Icons.smart_toy,
            signalGreen,
          ),

          _decisionItem(
            "Green Time",
            "$greenTime sec",
            Icons.timer,
            trafficBlue,
          ),

          _decisionItem(
            "Signal Action",
            signalSwitched
                ? "SWITCHED"
                : "STABLE",
            Icons.swap_horiz,
            signalSwitched
                ? signalYellow
                : signalGreen,
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // DECISION ITEM
  // ==========================================================

  Widget _decisionItem(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {

    return Container(

      margin:
          const EdgeInsets.only(bottom: 10),

      padding:
          const EdgeInsets.all(12),

      decoration: BoxDecoration(
        color:
            Colors.black.withOpacity(0.12),

        borderRadius:
            BorderRadius.circular(12),
      ),

      child: Row(
        children: [

          Icon(
            icon,
            color: color,
            size: 20,
          ),

          const SizedBox(width: 12),

          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                color: Colors.white54,
                fontSize: 12,
              ),
            ),
          ),

          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 13,
              fontWeight:
                  FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // PEDESTRIAN CARD
  // ==========================================================

  Widget _buildPedestrianCard(
    int total,
    int waiting,
    int crossing,
  ) {

    return Container(

      width: double.infinity,

      padding:
          const EdgeInsets.all(18),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(18),

        border: Border.all(
          color:
              pedestrianPurple
                  .withOpacity(0.25),
        ),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Row(
            children: [

              Container(
                padding:
                    const EdgeInsets.all(9),

                decoration:
                    BoxDecoration(
                  color:
                      pedestrianPurple
                          .withOpacity(0.10),
                  borderRadius:
                      BorderRadius.circular(10),
                ),

                child: const Icon(
                  Icons.directions_walk,
                  color: pedestrianPurple,
                ),
              ),

              const SizedBox(width: 10),

              const Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,

                  children: [

                    Text(
                      "Pedestrian Monitor",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                      ),
                    ),

                    Text(
                      "Crossing and waiting status",
                      style: TextStyle(
                        color: Colors.white54,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 18),

          Row(
            children: [

              Expanded(
                child: _pedestrianMetric(
                  "Detected",
                  "$total",
                  Icons.groups,
                ),
              ),

              const SizedBox(width: 10),

              Expanded(
                child: _pedestrianMetric(
                  "Waiting",
                  "$waiting",
                  Icons.hourglass_top,
                ),
              ),

              const SizedBox(width: 10),

              Expanded(
                child: _pedestrianMetric(
                  "Crossing",
                  "$crossing",
                  Icons.directions_walk,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // PEDESTRIAN METRIC
  // ==========================================================

  Widget _pedestrianMetric(
    String title,
    String value,
    IconData icon,
  ) {

    return Container(

      padding:
          const EdgeInsets.all(13),

      decoration: BoxDecoration(
        color:
            pedestrianPurple.withOpacity(
          0.07,
        ),

        borderRadius:
            BorderRadius.circular(12),
      ),

      child: Column(
        children: [

          Icon(
            icon,
            color: pedestrianPurple,
            size: 21,
          ),

          const SizedBox(height: 7),

          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 2),

          Text(
            title,
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // SYSTEM STATUS
  // ==========================================================

  Widget _buildSystemStatusCard() {

    final String fastapi =
        systemData["fastapi"] ??
            (apiOnline ? "ONLINE" : "OFFLINE");

    final String ai =
        systemData["ai_engine"] ??
            "ACTIVE";

    final String sumo =
        systemData["sumo"] ??
            "CONNECTED";

    final String yolo =
        systemData["yolo"] ??
            "READY";

    return Container(

      width: double.infinity,

      padding:
          const EdgeInsets.all(18),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(18),

        border: Border.all(
          color:
              signalGreen.withOpacity(
            0.18,
          ),
        ),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          const Row(
            children: [

              Icon(
                Icons.memory,
                color: signalGreen,
              ),

              SizedBox(width: 10),

              Text(
                "System Status",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          _systemStatusRow(
            "FastAPI Backend",
            fastapi,
            Icons.api,
          ),

          _systemStatusRow(
            "AI Engine",
            ai,
            Icons.smart_toy,
          ),

          _systemStatusRow(
            "SUMO + TraCI",
            sumo,
            Icons.traffic,
          ),

          _systemStatusRow(
            "YOLO Detection",
            yolo,
            Icons.camera_alt,
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // SYSTEM STATUS ROW
  // ==========================================================

  Widget _systemStatusRow(
    String title,
    String status,
    IconData icon,
  ) {

    final bool online =
        status.toUpperCase() == "ONLINE" ||
        status.toUpperCase() == "ACTIVE" ||
        status.toUpperCase() == "CONNECTED" ||
        status.toUpperCase() == "READY";

    return Container(

      margin:
          const EdgeInsets.only(bottom: 8),

      padding:
          const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 11,
      ),

      decoration: BoxDecoration(
        color:
            Colors.black.withOpacity(0.10),

        borderRadius:
            BorderRadius.circular(10),
      ),

      child: Row(
        children: [

          Icon(
            icon,
            color: Colors.white54,
            size: 19,
          ),

          const SizedBox(width: 10),

          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
              ),
            ),
          ),

          Icon(
            Icons.circle,
            size: 8,
            color: online
                ? signalGreen
                : signalRed,
          ),

          const SizedBox(width: 6),

          Text(
            status,
            style: TextStyle(
              color: online
                  ? signalGreen
                  : signalRed,
              fontSize: 10,
              fontWeight:
                  FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // SIMULATION CARD
  // ==========================================================

  Widget _buildSimulationCard(
    double simulationTime,
    String activeSignal,
    String priority,
  ) {

    return Container(

      width: double.infinity,

      padding:
          const EdgeInsets.all(18),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(18),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          const Row(
            children: [

              Icon(
                Icons.timeline,
                color: trafficBlue,
              ),

              SizedBox(width: 10),

              Text(
                "Simulation Status",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          const SizedBox(height: 15),

          Row(
            children: [

              Expanded(
                child: _simulationMetric(
                  "Simulation Time",
                  "${simulationTime.toStringAsFixed(1)} s",
                ),
              ),

              Expanded(
                child: _simulationMetric(
                  "Active Signal",
                  activeSignal,
                ),
              ),

              Expanded(
                child: _simulationMetric(
                  "Priority",
                  priority,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // SIMULATION METRIC
  // ==========================================================

  Widget _simulationMetric(
    String title,
    String value,
  ) {

    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,

      children: [

        Text(
          title,
          style: const TextStyle(
            color: Colors.white38,
            fontSize: 10,
          ),
        ),

        const SizedBox(height: 5),

        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 13,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }


  // ==========================================================
  // CAMERAS PAGE
  // ==========================================================

  Widget _buildCamerasPage() {

    final cameras = [

      {
        "name": "North Camera",
        "direction": "NORTH",
      },

      {
        "name": "South Camera",
        "direction": "SOUTH",
      },

      {
        "name": "East Camera",
        "direction": "EAST",
      },

      {
        "name": "West Camera",
        "direction": "WEST",
      },
    ];


    return SingleChildScrollView(

      padding:
          const EdgeInsets.all(16),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          _sectionHeader(
            "Traffic Cameras",
            "Four-way intersection monitoring",
            Icons.videocam,
          ),

          const SizedBox(height: 20),

          GridView.builder(

            shrinkWrap: true,

            physics:
                const NeverScrollableScrollPhysics(),

            itemCount: cameras.length,

            gridDelegate:
                const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.15,
            ),

            itemBuilder:
                (context, index) {

              final camera =
                  cameras[index];

              return _cameraCard(
                camera["name"]!,
                camera["direction"]!,
              );
            },
          ),

          const SizedBox(height: 20),

          _cameraInfoCard(),
        ],
      ),
    );
  }


  // ==========================================================
  // CAMERA CARD
  // ==========================================================

  Widget _cameraCard(
    String name,
    String direction,
  ) {

    return Container(

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),

        border: Border.all(
          color:
              aiCyan.withOpacity(0.18),
        ),
      ),

      child: Column(
        children: [

          Expanded(
            child: Container(

              width: double.infinity,

              decoration: BoxDecoration(
                color: roadDark,

                borderRadius:
                    const BorderRadius.vertical(
                  top: Radius.circular(16),
                ),
              ),

              child: Stack(
                alignment:
                    Alignment.center,

                children: [

                  const Icon(
                    Icons.videocam_outlined,
                    color: aiCyan,
                    size: 55,
                  ),

                  Positioned(
                    top: 10,
                    right: 10,

                    child: Container(
                      padding:
                          const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),

                      decoration:
                          BoxDecoration(
                        color:
                            signalGreen.withOpacity(
                          0.12,
                        ),

                        borderRadius:
                            BorderRadius.circular(
                          20,
                        ),
                      ),

                      child: const Row(
                        children: [

                          Icon(
                            Icons.circle,
                            color: signalGreen,
                            size: 7,
                          ),

                          SizedBox(width: 5),

                          Text(
                            "LIVE",
                            style: TextStyle(
                              color: signalGreen,
                              fontSize: 9,
                              fontWeight:
                                  FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          Padding(
            padding:
                const EdgeInsets.all(12),

            child: Row(
              children: [

                const Icon(
                  Icons.camera_alt,
                  color: aiCyan,
                  size: 20,
                ),

                const SizedBox(width: 9),

                Expanded(
                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment.start,

                    children: [

                      Text(
                        name,
                        style:
                            const TextStyle(
                          color: Colors.white,
                          fontWeight:
                              FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),

                      const SizedBox(height: 3),

                      Text(
                        direction,
                        style:
                            const TextStyle(
                          color: Colors.white54,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                ),

                const Icon(
                  Icons.circle,
                  color: signalGreen,
                  size: 8,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // CAMERA INFORMATION
  // ==========================================================

  Widget _cameraInfoCard() {

    return Container(

      width: double.infinity,

      padding:
          const EdgeInsets.all(18),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),

        border: Border.all(
          color:
              aiCyan.withOpacity(0.20),
        ),
      ),

      child: const Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Row(
            children: [

              Icon(
                Icons.smart_toy,
                color: aiCyan,
              ),

              SizedBox(width: 10),

              Text(
                "AI Vision System",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          SizedBox(height: 12),

          Text(
            "YOLO vehicle detection analyzes "
            "camera feeds to estimate vehicle "
            "count, queue length and traffic "
            "density.",
            style: TextStyle(
              color: Colors.white60,
              height: 1.5,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // ANALYTICS PAGE
  // ==========================================================

  Widget _buildAnalyticsPage() {

    final directions =
        (trafficData["directions"] ?? {})
            as Map<String, dynamic>;

    final int vehicles =
        trafficData["vehicles_detected"] ?? 0;

    final int pedestrians =
        trafficData["pedestrians_detected"] ?? 0;

    final String traffic =
        trafficData["traffic_status"] ??
            "UNKNOWN";

    final String priority =
        trafficData["priority_direction"] ??
            "UNKNOWN";


    return SingleChildScrollView(

      padding:
          const EdgeInsets.all(16),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          _sectionHeader(
            "Traffic Analytics",
            "Real-time traffic intelligence",
            Icons.analytics,
          ),

          const SizedBox(height: 20),

          Row(
            children: [

              Expanded(
                child: _analyticsCard(
                  "Vehicles",
                  "$vehicles",
                  Icons.directions_car,
                  trafficBlue,
                ),
              ),

              const SizedBox(width: 10),

              Expanded(
                child: _analyticsCard(
                  "Pedestrians",
                  "$pedestrians",
                  Icons.directions_walk,
                  pedestrianPurple,
                ),
              ),
            ],
          ),

          const SizedBox(height: 10),

          Row(
            children: [

              Expanded(
                child: _analyticsCard(
                  "Traffic",
                  traffic,
                  Icons.traffic,
                  _trafficStatusColor(
                    traffic,
                  ),
                ),
              ),

              const SizedBox(width: 10),

              Expanded(
                child: _analyticsCard(
                  "Priority",
                  priority,
                  Icons.priority_high,
                  signalGreen,
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          const Text(
            "Direction Analysis",
            style: TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 12),

          _directionAnalytics(
            "NORTH",
            directions["NORTH"],
          ),

          _directionAnalytics(
            "SOUTH",
            directions["SOUTH"],
          ),

          _directionAnalytics(
            "EAST",
            directions["EAST"],
          ),

          _directionAnalytics(
            "WEST",
            directions["WEST"],
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // ANALYTICS CARD
  // ==========================================================

  Widget _analyticsCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {

    return Container(

      padding:
          const EdgeInsets.all(16),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),

        border: Border.all(
          color:
              color.withOpacity(0.20),
        ),
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Icon(
            icon,
            color: color,
            size: 27,
          ),

          const SizedBox(height: 12),

          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 4),

          Text(
            title,
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // DIRECTION ANALYTICS
  // ==========================================================

  Widget _directionAnalytics(
    String direction,
    dynamic rawData,
  ) {

    if (rawData == null) {
      return const SizedBox();
    }

    final data =
        Map<String, dynamic>.from(
      rawData,
    );

    final int vehicles =
        data["vehicles"] ?? 0;

    final int queue =
        data["queue"] ?? 0;

    final double waiting =
        (data["waiting_time"] ?? 0)
            .toDouble();

    final String status =
        data["status"] ?? "UNKNOWN";

    final Color statusColor =
        _trafficStatusColor(status);


    return Container(

      margin:
          const EdgeInsets.only(bottom: 12),

      padding:
          const EdgeInsets.all(16),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),
      ),

      child: Column(
        children: [

          Row(
            children: [

              Container(
                padding:
                    const EdgeInsets.all(9),

                decoration:
                    BoxDecoration(
                  color:
                      aiCyan.withOpacity(0.10),

                  borderRadius:
                      BorderRadius.circular(10),
                ),

                child: const Icon(
                  Icons.alt_route,
                  color: aiCyan,
                  size: 20,
                ),
              ),

              const SizedBox(width: 12),

              Expanded(
                child: Text(
                  direction,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ),

              Container(
                padding:
                    const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 5,
                ),

                decoration:
                    BoxDecoration(
                  color:
                      statusColor.withOpacity(
                    0.12,
                  ),

                  borderRadius:
                      BorderRadius.circular(20),
                ),

                child: Text(
                  status,
                  style: TextStyle(
                    color: statusColor,
                    fontSize: 10,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 15),

          Row(
            mainAxisAlignment:
                MainAxisAlignment.spaceBetween,

            children: [

              _miniMetric(
                "Vehicles",
                "$vehicles",
                Icons.directions_car,
              ),

              _miniMetric(
                "Queue",
                "$queue",
                Icons.queue,
              ),

              _miniMetric(
                "Waiting",
                "${waiting.toStringAsFixed(1)}s",
                Icons.timer,
              ),
            ],
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // MINI ANALYTICS METRIC
  // ==========================================================

  Widget _miniMetric(
    String title,
    String value,
    IconData icon,
  ) {

    return Column(
      children: [

        Icon(
          icon,
          size: 18,
          color: Colors.white54,
        ),

        const SizedBox(height: 5),

        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),

        const SizedBox(height: 3),

        Text(
          title,
          style: const TextStyle(
            color: Colors.white38,
            fontSize: 10,
          ),
        ),
      ],
    );
  }


  // ==========================================================
  // SETTINGS PAGE
  // ==========================================================

  Widget _buildSettingsPage() {

    return SingleChildScrollView(

      padding:
          const EdgeInsets.all(16),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          _sectionHeader(
            "System Settings",
            "Smart Traffic AI configuration",
            Icons.settings,
          ),

          const SizedBox(height: 24),

          _settingTile(
            Icons.light_mode,
            "Theme Mode",
            "Switch between light and dark interface",
            AppThemeController.themeMode.value == ThemeMode.dark,
            pedestrianPurple,
            onChanged: (value) {
              AppThemeController.setThemeMode(
                value ? ThemeMode.dark : ThemeMode.light,
              );
            },
          ),

          _settingTile(
            Icons.notifications_active,
            "Traffic Alerts",
            "Receive congestion alerts",
            true,
            warningOrange,
          ),

          const SizedBox(height: 20),

          _systemInformationCard(),
        ],
      ),
    );
  }


  // ==========================================================
  // SETTINGS TILE
  // ==========================================================

  Widget _settingTile(
    IconData icon,
    String title,
    String subtitle,
    bool value,
    Color color, {
    void Function(bool)? onChanged,
  }) {

    return Container(

      margin:
          const EdgeInsets.only(bottom: 12),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),
      ),

      child: ListTile(

        contentPadding:
            const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 5,
        ),

        leading: Container(

          padding:
              const EdgeInsets.all(10),

          decoration: BoxDecoration(
            color:
                color.withOpacity(0.12),

            borderRadius:
                BorderRadius.circular(12),
          ),

          child: Icon(
            icon,
            color: color,
          ),
        ),

        title: Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),

        subtitle: Text(
          subtitle,
          style: const TextStyle(
            color: Colors.white54,
            fontSize: 11,
          ),
        ),

        trailing: Switch(
          value: value,

          onChanged: onChanged ?? (_) {},

          activeColor: signalGreen,
        ),
      ),
    );
  }


  // ==========================================================
  // SYSTEM INFORMATION
  // ==========================================================

  Widget _systemInformationCard() {

    return Container(

      width: double.infinity,

      padding:
          const EdgeInsets.all(18),

      decoration: BoxDecoration(
        color: trafficPanel,

        borderRadius:
            BorderRadius.circular(16),
      ),

      child: const Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [

          Text(
            "System Information",
            style: TextStyle(
              color: Colors.white,
              fontSize: 17,
              fontWeight: FontWeight.bold,
            ),
          ),

          SizedBox(height: 12),

          Text(
            "Smart Traffic AI\n"
            "Version 1.0\n\n"
            "Frontend: Flutter\n"
            "Backend: FastAPI + Python\n"
            "AI: YOLO + OpenCV\n"
            "Simulation: SUMO + TraCI",
            style: TextStyle(
              color: Colors.white54,
              height: 1.6,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }


  // ==========================================================
  // TRAFFIC STATUS COLOR
  // ==========================================================

  Color _trafficStatusColor(
    String status,
  ) {

    switch (
        status.toUpperCase()) {

      case "HIGH":
        return signalRed;

      case "MEDIUM":
        return signalYellow;

      case "LOW":
        return signalGreen;

      default:
        return Colors.white54;
    }
  }
}