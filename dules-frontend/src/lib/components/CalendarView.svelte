<script lang="ts">
    import { onMount } from "svelte";
    import { Calendar } from "@fullcalendar/core/index.js";
    import dayGridPlugin from "@fullcalendar/daygrid";
    import interactionPlugin from '@fullcalendar/interaction';
    import type { Schedule } from "$lib/types";

    // 상위에서 전달한 schedules와 onEventclick의 값을  하부 컴포넌트에서 받기??
    let { schedules, onEventClick } = $props<{
        schedules: Schedule[],
        onEventClick: (schedule: Schedule) => void
    }>();

    let calendarEl!: HTMLElement;
    let calendar: Calendar | null = null;

    let calendarEvents = $derived(schedules.map((s:Schedule) => {
        let eventColor = '';

        if (s.type === 'EVENT') {
            eventColor = '#10b981';
        } else if (s.type === 'TASK') {
            eventColor = '#ef4444';
        } else {
        }

        return {
            id: s.id,
            title: s.title,
            start: s.start_at || s.deadline || s.created_at,
            end: s.end_at || undefined,
            allDay: s.type === 'TASK',
            display: 'block',
            backgroundColor: eventColor,
            borderColor: 'transparent',
            textColor: '#ffffff',
            extendedProps: { originalData: s }
        };
    }));

    onMount(() => {
        calendar = new Calendar(calendarEl, {
            plugins: [dayGridPlugin, interactionPlugin],
            initialView: 'dayGridMonth',

            displayEventTime: false,
            
            headerToolbar: {
                left: 'prev',
                center: 'title',
                right: 'next'
            },
            events: calendarEvents,
            eventClick: (info) => {
                onEventClick(info.event.extendedProps.originalData);
            },
            height: 'auto',
            contentHeight: 'auto',
            fixedWeekCount: false
        });

        calendar.render();

        return () => {
            calendar?.destroy();
        };
    });

    $effect(() => {
        if (calendar) {
            calendar.removeAllEvents();
            calendar.addEventSource(calendarEvents);
        }
    });
    
</script>

<div bind:this={calendarEl} class="calendar-container"></div>

<style>

    .calendar-container {
        font-family: inherit;
    }

    :global(.fc) {
        font-size: 0.8rem;
    }

    :global(.fc .fc-toolbar-title) {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1f2937;
    }

    :global(.fc .fc-event-title) {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: block !important;
        font-weight: 500 !important;
    }

    :global(.fc .fc-event-main) {
        padding: 2px 4px !important;
    }

    :global(.fc .fc-event) {
        cursor: pointer;
        border-radius: 4px;
        margin-bottom: 3px !important;
        border: none;
    }

</style>