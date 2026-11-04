import { SectionHeader } from '../shared/SectionHeader';
import { RuledField } from '../shared/RuledField';
import type { DailyPage } from '../../api/planner';

interface NotesSidebarProps {
  page: DailyPage;
  onChange: (patch: Partial<DailyPage>) => void;
  onBlur: (patch: Partial<DailyPage>) => void;
}

export function NotesSidebar({ page, onChange, onBlur }: NotesSidebarProps) {
  return (
    <div>
      <section>
        <SectionHeader label="Notes" />
        <RuledField
          rows={8}
          value={page.notes}
          onChange={(e) => onChange({ notes: e.target.value })}
          onBlur={() => onBlur({ notes: page.notes })}
          aria-label="Notes"
        />
      </section>

      <section>
        <SectionHeader label="Study Topic" />
        <RuledField
          rows={3}
          value={page.study_topic}
          onChange={(e) => onChange({ study_topic: e.target.value })}
          onBlur={() => onBlur({ study_topic: page.study_topic })}
          aria-label="Study Topic"
        />
      </section>

      <section>
        <SectionHeader label="Exercise Plan" />
        <RuledField
          rows={3}
          value={page.exercise_plan}
          onChange={(e) => onChange({ exercise_plan: e.target.value })}
          onBlur={() => onBlur({ exercise_plan: page.exercise_plan })}
          aria-label="Exercise Plan"
        />
      </section>

      <section>
        <SectionHeader label="Goals for Today" />
        <RuledField
          rows={3}
          value={page.goals_for_today}
          onChange={(e) => onChange({ goals_for_today: e.target.value })}
          onBlur={() => onBlur({ goals_for_today: page.goals_for_today })}
          aria-label="Goals for Today"
        />
      </section>

      <section>
        <SectionHeader label="To Do List" />
        <RuledField
          rows={5}
          value={page.to_do_list}
          onChange={(e) => onChange({ to_do_list: e.target.value })}
          onBlur={() => onBlur({ to_do_list: page.to_do_list })}
          aria-label="To Do List"
        />
      </section>
    </div>
  );
}
