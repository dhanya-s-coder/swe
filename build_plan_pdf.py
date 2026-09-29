from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

out = 'output/pdf/factory_adjuster_simulation_implementation_plan.pdf'
doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=15*mm)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Title2', parent=styles['Title'], fontSize=19, leading=23, alignment=TA_CENTER, textColor=colors.HexColor('#12355B'), spaceAfter=8))
styles.add(ParagraphStyle(name='Sub', parent=styles['Normal'], fontSize=9.5, leading=13, alignment=TA_CENTER, textColor=colors.HexColor('#4A5568'), spaceAfter=14))
styles.add(ParagraphStyle(name='H', parent=styles['Heading2'], fontSize=13, leading=16, textColor=colors.HexColor('#12355B'), spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle(name='Body2', parent=styles['BodyText'], fontSize=9.2, leading=13, spaceAfter=5))
styles.add(ParagraphStyle(name='Small', parent=styles['BodyText'], fontSize=8.3, leading=11))

def P(txt, style='Body2'):
    return Paragraph(txt, styles[style])

story = []
story += [P('Factory Machine Failure and Adjuster Assignment', 'Title2'), P('Verified implementation plan based on the problem statement and meeting transcript', 'Sub')]
story += [P('1. Correct interpretation of the problem statement', 'H')]
story += [P('When a machine fails, the <b>service manager assigns the failed machine to an available adjuster</b>. The term used in the problem statement is adjuster, so this plan uses adjuster consistently. Adjusters may be trained for one or more machine categories. The service manager maintains one shared queue: when machines are waiting it contains machines; when no machine is waiting it contains idle adjusters. The first compatible machine and adjuster are matched whenever possible.', 'Body2')]
story += [P('2. System objective', 'H')]
story += [P('Simulate machine failures and repairs, measure machine and adjuster utilization, and determine the average performance and suitable number of adjusters for the factory.', 'Body2')]
story += [P('3. Main components', 'H')]
data = [
    ['Component', 'Responsibility'],
    ['Machine Manager', 'Creates machines, schedules failures, and tracks running, failed, waiting, and repaired states.'],
    ['Failure Generator', 'Generates the next failure time using the selected probability distribution and each category MTTF.'],
    ['Service Manager', 'Receives failures, creates tickets, maintains the shared queue, and assigns compatible available adjusters.'],
    ['Adjuster Manager', 'Tracks adjuster skills, busy/idle status, repair start and completion times.'],
    ['Event Queue', 'Processes failure and repair-completion events in chronological order.'],
    ['Database', 'Stores machine categories, skills, adjusters, failures, repairs, tickets, and simulation results.'],
    ['Dashboard', 'Displays live status, queue, downtime, utilization, and staffing comparisons.'],
]
t = Table([[P(c, 'Small') for c in row] for row in data], colWidths=[42*mm, 132*mm], repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#12355B')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#B8C4D1')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#F3F6F9')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
story += [t]
story += [P('4. Assignment and queue logic', 'H')]
story += [P('<b>On machine failure:</b> create a repair ticket; find an idle adjuster with the required skill; if one is available, assign the machine immediately; otherwise put the machine in the waiting queue.', 'Body2'), P('<b>On adjuster availability:</b> select the first waiting machine that the adjuster can repair, assign it, and start the repair. If no compatible machine is waiting, place the idle adjuster in the shared queue. This preserves the problem statement rule that only one of the two queues needs to be maintained at a time.', 'Body2')]
story += [P('5. Data model', 'H')]
data2 = [['Entity', 'Important fields'], ['Machine', 'machine_id, category, MTTF, status, failure_count, uptime, downtime'], ['Adjuster', 'adjuster_id, skill_set, status, busy_time, repairs_completed'], ['Skill', 'skill_id, machine_category, repair_time_distribution'], ['Ticket', 'ticket_id, machine_id, required_skill, priority, status, timestamps'], ['Event', 'event_time, event_type, machine_id, adjuster_id'], ['SimulationRun', 'run_id, seed, duration, adjuster_count, metric results']]
t2=Table([[P(c,'Small') for c in row] for row in data2], colWidths=[38*mm,136*mm], repeatRows=1)
t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2E6F95')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#B8C4D1')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#F3F6F9')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
story += [t2]
story += [PageBreak(), P('6. Probability and simulation model', 'H')]
story += [P('Use a discrete-event simulation. The event calendar stores machine-failure and repair-completion events. For failure intervals, exponential or Weibull distributions are statistically suitable because time is non-negative and failures are event arrivals. If the academic requirement specifically mandates Gaussian pseudo-random values, use a truncated Gaussian so negative times are rejected. Repair times can use a Gaussian distribution with a minimum value or another documented distribution.', 'Body2')]
story += [P('Each simulation run should use a random seed, run for a fixed duration, and be repeated many times. Compare candidate adjuster counts, for example 2 through 20, rather than relying on one run.', 'Body2')]
story += [P('7. Metrics and dashboard', 'H')]
for x in ['Machine utilization = running time / total simulation time', 'Adjuster utilization = busy time / total simulation time', 'Average machine waiting time before assignment', 'Average repair time and total downtime', 'Queue length over time and unresolved tickets', 'Failures and downtime by machine category', 'Comparison of performance for each adjuster count']:
    story.append(P('&bull; '+x, 'Body2'))
story += [P('8. Technology recommendation', 'H'), P('<b>Python, SimPy, NumPy, pandas, SQLite, Streamlit, Plotly, and scikit-learn.</b> Start with Python + SimPy + SQLite + Streamlit. Add machine learning only after simulation metrics and assignment rules have been validated.', 'Body2')]
story += [P('9. Delivery phases', 'H')]
phases = [['Phase 1', 'Finalize machine categories, MTTF, repair distributions, adjuster skills, queue policy, and metrics.'], ['Phase 2', 'Implement machines, adjusters, event queue, failure generation, repair completion, and skill-based assignment.'], ['Phase 3', 'Add database persistence and the ticket lifecycle: OPEN, WAITING, ASSIGNED, IN_REPAIR, RESOLVED.'], ['Phase 4', 'Build dashboard for status, queue, downtime, utilization, and adjuster-count comparison.'], ['Phase 5', 'Generate simulation data and add failure-risk or repair-duration prediction models.'], ['Phase 6', 'Validate with repeated runs and prepare architecture, ER, activity, and event-flow diagrams.']]
t3=Table([[P(c,'Small') for c in row] for row in phases], colWidths=[25*mm,149*mm])
t3.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#B8C4D1')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.white, colors.HexColor('#F3F6F9')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
story += [t3, P('10. Minimum viable prototype', 'H'), P('Use 3 machine categories, 10-20 machines, 3-5 adjusters, skill-based assignment, one shared queue, random failures, random repair times, repair tickets, and a basic dashboard. After this works, add prediction, backup handling, and advanced analytics.', 'Body2')]
story += [P('Implementation rule to preserve', 'H'), P('Machine failure -> service manager -> compatible available adjuster. If no compatible adjuster is free, the machine waits. When an adjuster becomes free, the service manager assigns the next compatible waiting machine.', 'Body2')]

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('Helvetica', 8); canvas.setFillColor(colors.HexColor('#718096'))
    canvas.drawString(16*mm, 9*mm, 'Factory Adjuster Simulation - Implementation Plan')
    canvas.drawRightString(A4[0]-16*mm, 9*mm, f'Page {doc.page}')
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(out)
