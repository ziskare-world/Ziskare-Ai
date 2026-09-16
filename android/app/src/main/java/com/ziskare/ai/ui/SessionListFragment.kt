package com.ziskare.ai.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.ziskare.ai.R
import com.ziskare.ai.db.entity.Session
import com.ziskare.ai.ui.adapter.SessionAdapter
import com.ziskare.ai.viewmodel.SessionViewModel
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class SessionListFragment(
    private val onSessionSelected: (Session) -> Unit
) : Fragment() {

    private val vm: SessionViewModel by activityViewModels()

    override fun onCreateView(inf: LayoutInflater, c: ViewGroup?, s: Bundle?): View =
        inf.inflate(R.layout.fragment_session_list, c, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val adapter = SessionAdapter(
            onClick = onSessionSelected,
            onLongClick = { s -> showRenameDialog(s); true },
            onDelete = { s ->
                AlertDialog.Builder(requireContext())
                    .setTitle("Delete Chat")
                    .setMessage("Delete \"${s.title}\"? This cannot be undone.")
                    .setPositiveButton("Delete") { _, _ -> vm.deleteSession(s) }
                    .setNegativeButton("Cancel", null).show()
            }
        )

        view.findViewById<RecyclerView>(R.id.rvSessions).apply {
            layoutManager = LinearLayoutManager(requireContext())
            this.adapter = adapter
        }

        view.findViewById<FloatingActionButton>(R.id.fabNewChat).setOnClickListener {
            onSessionSelected(vm.createSession())
        }

        viewLifecycleOwner.lifecycleScope.launch {
            vm.sessions.collectLatest { adapter.submitList(it) }
        }
    }

    private fun showRenameDialog(session: Session) {
        val input = EditText(requireContext()).apply {
            setText(session.title)
            setPadding(48, 24, 48, 8)
        }
        AlertDialog.Builder(requireContext())
            .setTitle("Rename Chat")
            .setView(input)
            .setPositiveButton("Rename") { _, _ ->
                input.text.toString().trim().takeIf { it.isNotBlank() }
                    ?.let { vm.renameSession(session.id, it) }
            }
            .setNegativeButton("Cancel", null).show()
    }
}
